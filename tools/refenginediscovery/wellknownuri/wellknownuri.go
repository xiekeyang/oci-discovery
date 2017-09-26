// Copyright 2017 oci-discovery contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package wellknownuri

import (
	"encoding/json"
	"fmt"
	"mime"
	"net/http"
	"net/url"

	"github.com/sirupsen/logrus"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery/xdg"
	"golang.org/x/net/context"
)

// Engine implements the OCI Ref-Engine Discovery protocol.
type Engine struct {
	protocols []string
}

// New creates a new ref-engine-discovery instance.
func New(ctx context.Context, protocols []string) (engine refenginediscovery.Engine, err error) {
	if protocols == nil || len(protocols) == 0 {
		protocols = []string{"https", "http"}
	}

	return &Engine{
		protocols: protocols,
	}, nil
}

// RefEngines calculates ref engines using OCI Ref-Engine Discovery
// and calls refEngineCallback on each one.  RefEngines returns any
// errors returned by refEngineCallback and aborts further iteration.
// Other errors (e.g. in fetching a ref-engine discovery object from a
// particular protocol/host pair) generate logged warnings but are
// otherwise ignored.
func (eng *Engine) RefEngines(ctx context.Context, name string, refEngineCallback refenginediscovery.RefEngineCallback) (err error) {
	parsedName, err := hostbasedimagenames.Parse(name)
	if err != nil {
		logrus.Warn(err)
		return nil
	}

	uri, err := url.Parse("https://example.com/.well-known/oci-host-ref-engines")
	if err != nil {
		logrus.Warn(err)
		return nil
	}
	for _, protocol := range eng.protocols {
		uri.Scheme = protocol
		// FIXME: walk DNS ancestors
		uri.Host = parsedName["host"]
		reference, err := eng.fetch(ctx, uri)
		if err != nil {
			logrus.Warn(err)
			continue
		}
		var casEngines []engine.Reference
		if reference.Engines.CASEngines != nil {
			casEngines = make([]engine.Reference, len(reference.Engines.CASEngines))
			for i, config := range reference.Engines.CASEngines {
				casEngines[i].Config = config
				casEngines[i].URI = reference.URI
			}
		}
		for _, config := range reference.Engines.RefEngines {
			ref := refenginediscovery.Reference{
				Config: engine.Reference{
					Config: config,
					URI:    reference.URI,
				},
				CASEngines: casEngines,
			}
			err = refEngineCallback(ctx, ref)
			if err != nil {
				return err
			}
		}
	}

	return nil
}

// Close releases resources held by the engine.
func (eng *Engine) Close(ctx context.Context) (err error) {
	return nil
}

func (eng *Engine) fetch(ctx context.Context, uri *url.URL) (ref *xdg.Reference, err error) {
	request := &http.Request{
		Method: "GET",
		URL:    uri,
		Header: map[string][]string{
			"Accept": {"application/vnd.oci.ref-engines.v1+json"},
		},
	}
	request = request.WithContext(ctx)

	client := &http.Client{}
	logrus.Debugf("requesting %s from %s", request.Header.Get(`Accept`), request.URL)
	response, err := client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	if response.StatusCode >= 400 {
		return nil, fmt.Errorf("ref engine fetching error, status code = %d", response.StatusCode)
	}

	mediatype, _, err := mime.ParseMediaType(response.Header.Get(`Content-Type`))
	if err != nil {
		return nil, err
	}

	if mediatype != request.Header.Get(`Accept`) {
		return nil, fmt.Errorf("requested %s from %s but got %s", request.Header.Get(`Accept`), request.URL, mediatype)
	}

	ref = &xdg.Reference{
		URI: uri, // FIXME: get URI after any redirects
	}
	if err := json.NewDecoder(response.Body).Decode(&ref.Engines); err != nil {
		logrus.Errorf("ref engines object decoded failed: %s", err)
		return nil, err
	}

	return ref, nil
}
