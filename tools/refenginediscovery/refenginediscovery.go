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

package refenginediscovery

import (
	"encoding/json"
	"fmt"
	"mime"
	"net/http"
	"net/url"

	"github.com/sirupsen/logrus"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"golang.org/x/net/context"
)

// Discover calculates ref engines using Ref-Engine Discovery and
// calls RefEngines on each one.  Discover returns any errors returned
// by RefEngines and aborts further iteration.  Other errors (e.g. in
// fetching a ref-engine discovery object from a particular
// protocol/host pair) generate logged warnings but are otherwise
// ignored.
func Discover(ctx context.Context, protocols []string, host string, refEngineCallback RefEngineCallback) (err error) {
	if protocols == nil || len(protocols) == 0 {
		protocols = []string{"https", "http"}
	}

	uri, err := url.Parse("https://example.com/.well-known/oci-host-ref-engines")
	if err != nil {
		return err
	}
	for _, protocol := range protocols {
		uri.Scheme = protocol
		// FIXME: walk DNS ancestors
		uri.Host = host
		base, err := fetch(ctx, uri)
		if err != nil {
			logrus.Warn(err)
			continue
		}
		err = base.RefEngines(ctx, refEngineCallback)
		if err != nil {
			return err
		}
	}

	return nil
}

func fetch(ctx context.Context, uri *url.URL) (base *Base, err error) {
	base = &Base{}
	client := &http.Client{}

	request := &http.Request{
		Method: "GET",
		URL:    uri,
		Header: map[string][]string{
			"Accept": {"application/vnd.oci.ref-engines.v1+json"},
		},
	}
	request = request.WithContext(ctx)

	logrus.Debugf("requesting %s from %s", request.Header.Get(`Accept`), request.URL)
	response, err := client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	base.URI = uri // FIXME: get URI after any redirects

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

	if err := json.NewDecoder(response.Body).Decode(&base.Config); err != nil {
		logrus.Errorf("ref engines object decoded failed: %s", err)
		return nil, err
	}

	return base, nil
}

// RefEngines constructs a ref engine for each Config.RefEngines entry
// and calls refEngineCallback on it.  RefEngines returns any errors
// returned by refEngineCallback and aborts further iteration.  Other
// errors (e.g. in failure to initialize a ref engine) generate logged
// warnings but are otherwise ignored.
func (base *Base) RefEngines(ctx context.Context, refEngineCallback RefEngineCallback) (err error) {
	for _, config := range base.Config.RefEngines {
		constructor, ok := refengine.Constructors[config.Protocol]
		if !ok {
			logrus.Debugf("unsupported ref-engine protocol %q (%v)", config.Protocol, refengine.Constructors)
			continue
		}
		engine, err := constructor(ctx, base.URI, config.Data)
		if err != nil {
			logrus.Warnf("failed to initialize %s ref engine with %v: %s", config.Protocol, config.Data, err)
			continue
		}
		resolvedCASEngines := make([]ResolvedCASEngine, len(base.Config.CASEngines))
		for i, config := range base.Config.CASEngines {
			resolvedCASEngines[i].Config = config
			resolvedCASEngines[i].URI = base.URI
		}
		err = refEngineCallback(ctx, engine, resolvedCASEngines)
		if err != nil {
			return err
		}
	}

	return nil
}
