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

package indextemplate

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"

	"github.com/jtacoma/uritemplates"
	//"github.com/opencontainers/image-spec/specs-go/v1"
	"github.com/sirupsen/logrus"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	v1 "github.com/xiekeyang/oci-discovery/tools/newimagespec"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"github.com/xiekeyang/oci-discovery/tools/util"
	"golang.org/x/net/context"
)

// Engine implements the OCI Index Template ref-engine protocol.
type Engine struct {
	uri  *uritemplates.UriTemplate
	base *url.URL
}

// New creates a new ref-engine instance.
func New(ctx context.Context, baseURI *url.URL, config interface{}) (engine refengine.Engine, err error) {
	configMap, ok := config.(map[string]string)
	if !ok {
		configMap2, ok := config.(map[string]interface{})
		if !ok {
			return nil, fmt.Errorf("index template config is not a map[string]string: %v", config)
		}
		uriInterface, ok := configMap2["uri"]
		if !ok {
			return nil, fmt.Errorf("index template config missing required 'uri' property: %v", configMap)
		}
		configMap = make(map[string]string)
		configMap["uri"], ok = uriInterface.(string)
		if !ok {
			return nil, fmt.Errorf("index template config 'uri' is not a string: %v", uriInterface)
		}
	}

	uriString, ok := configMap["uri"]
	if !ok {
		return nil, fmt.Errorf("index template config missing required 'uri' property: %v", configMap)
	}

	uriTemplate, err := uritemplates.Parse(uriString)
	if err != nil {
		return nil, err
	}

	return &Engine{
		uri:  uriTemplate,
		base: baseURI,
	}, nil
}

// Get returns an array of matching references from the store.
func (engine *Engine) Get(ctx context.Context, name string) (descriptors []v1.Descriptor, err error) {
	parsedName, err := hostbasedimagenames.Parse(name)
	if err != nil {
		return nil, err
	}

	uri, err := engine.resolveURI(parsedName)
	if err != nil {
		return nil, err
	}

	client := &http.Client{}

	request := &http.Request{
		Method: "GET",
		URL:    uri,
		Header: map[string][]string{
			"Accept": {"application/vnd.oci.image.index.v1+json"},
		},
	}
	request = request.WithContext(ctx)

	logrus.Debugf("requesting %s from %s", request.Header.Get("accept"), request.URL)
	response, err := client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	return engine.handleIndex(response, parsedName)
}

// Close releases resources held by the engine.
func (engine *Engine) Close(ctx context.Context) (err error) {
	return nil
}

func (engine *Engine) resolveURI(parsedName map[string]string) (uri *url.URL, err error) {
	referenceURI, err := engine.uri.Expand(util.StringStringToStringInterface(parsedName))
	if err != nil {
		return nil, err
	}

	parsedReference, err := url.Parse(referenceURI)
	if err != nil {
		return nil, err
	}

	uri = engine.base.ResolveReference(parsedReference)
	return uri, nil
}

func (engine *Engine) handleIndex(response *http.Response, parsedName map[string]string) (descriptors []v1.Descriptor, err error) {
	descriptors = make([]v1.Descriptor, 0)
	var index v1.Index

	// FIXME: check response content type (and charset?)

	if err := json.NewDecoder(response.Body).Decode(&index); err != nil {
		logrus.Errorf("%s claimed to return application/vnd.oci.image.index.v1+json, but the response schema did not match: %s", response.Request.URL, err)
		return descriptors, err
	}

	if fragment, ok := parsedName["fragment"]; ok && len(fragment) > 0 {
		for _, descriptor := range index.Manifests {
			if fragment == descriptor.Annotations[`org.opencontainers.image.ref.name`] {
				descriptors = append(descriptors, descriptor)
			}
		}
	} else {
		descriptors = append(descriptors, index.Manifests...)
	}

	return descriptors, nil
}

func init() {
	refengine.Constructors["oci-index-template-v1"] = New
}
