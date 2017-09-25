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
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"testing"

	v1 "github.com/opencontainers/image-spec/specs-go/v1"
	"github.com/stretchr/testify/assert"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	v1new "github.com/xiekeyang/oci-discovery/tools/newimagespec"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"golang.org/x/net/context"
)

func TestNewFromEngineConfigGood(t *testing.T) {
	ctx := context.Background()
	config := engine.Config{
		Data: map[string]interface{}{
			"uri": "a/b",
		},
	}
	base, err := url.Parse("https://example.com")
	if err != nil {
		t.Fatal(err)
	}

	engine, err := New(ctx, base, config.Data)
	if err != nil {
		t.Fatal(err)
	}

	err = engine.Close(ctx)
	if err != nil {
		t.Fatal(err)
	}
}

func TestNewFromConfigBad(t *testing.T) {
	ctx := context.Background()
	base, err := url.Parse("https://example.com")
	if err != nil {
		t.Fatal(err)
	}

	for _, testcase := range []struct {
		name     string
		config   interface{}
		expected string
	}{
		{
			name:     "config not a map",
			config:   "not a map",
			expected: `index template config is not a map\[string\]string: .*`,
		},
		{
			name:     "string->string config missing 'uri' property",
			config:   map[string]string{},
			expected: `index template config missing required 'uri' property: .*`,
		},
		{
			name:     "string->interface config missing 'uri' property",
			config:   map[string]interface{}{},
			expected: `index template config missing required 'uri' property: .*`,
		},
		{
			name: "uri not a string",
			config: map[string]interface{}{
				"uri": 1,
			},
			expected: `index template config 'uri' is not a string: .*`,
		},
		{
			name: "uri string not a URI Template",
			config: map[string]string{
				"uri": "{",
			},
			expected: `malformed template`,
		},
	} {
		t.Run(testcase.name, func(t *testing.T) {
			_, err := New(ctx, base, testcase.config)
			if err == nil {
				t.Fatalf("expected %s", testcase.expected)
			}
			assert.Regexp(t, testcase.expected, err.Error())
		})
	}
}

func TestGetPreFetchGood(t *testing.T) {
	ctx := context.Background()
	parsedName, err := hostbasedimagenames.Parse("example.com/a#1.0")
	if err != nil {
		t.Fatal(err)
	}
	for _, testcase := range []struct {
		template string
		base     string
		expected string
	}{
		{
			template: "index.json",
			base:     "https://example.com/a",
			expected: "https://example.com/index.json",
		},
		{
			template: "index.json",
			base:     "https://example.com/a/",
			expected: "https://example.com/a/index.json",
		},
		{
			template: "https://{host}/{path}#{fragment}",
			base:     "https://a.example.com/b/",
			expected: "https://example.com/a#1.0",
		},
		{
			template: "//{host}/{path}#{fragment}",
			base:     "https://a.example.com/b/",
			expected: "https://example.com/a#1.0",
		},
		{
			template: "/{path}#{fragment}",
			base:     "https://b.example.com/c/",
			expected: "https://b.example.com/a#1.0",
		},
		{
			template: "{path}#{fragment}",
			base:     "https://b.example.com/c/",
			expected: "https://b.example.com/c/a#1.0",
		},
		{
			template: "#{fragment}",
			base:     "https://example.com/a",
			expected: "https://example.com/a#1.0",
		},
		{
			template: "#{fragment}",
			base:     "https://example.com/a/",
			expected: "https://example.com/a/#1.0",
		},
	} {
		name := fmt.Sprintf("%s from %s", testcase.template, testcase.base)
		t.Run(name, func(t *testing.T) {
			base, err := url.Parse(testcase.base)
			if err != nil {
				t.Fatal(err)
			}

			config := map[string]string{
				"uri": testcase.template,
			}

			engine, err := New(ctx, base, config)
			if err != nil {
				t.Fatal(err)
			}
			defer engine.Close(ctx)

			request, err := engine.(*Engine).getPreFetch(parsedName)
			if err != nil {
				t.Fatal(err)
			}

			uri, err := url.Parse(testcase.expected)
			if err != nil {
				t.Fatal(err)
			}

			expected := &http.Request{
				Method: "GET",
				URL:    uri,
				Header: map[string][]string{
					"Accept": {"application/vnd.oci.image.index.v1+json"},
				},
			}

			assert.Equal(t, expected, request)
		})
	}
}

func TestGetPreFetchBad(t *testing.T) {
	ctx := context.Background()
	config := map[string]string{
		"uri": "{+path}",
	}

	base, err := url.Parse("https://example.com")
	if err != nil {
		t.Fatal(err)
	}

	engine, err := New(ctx, base, config)
	if err != nil {
		t.Fatal(err)
	}
	defer engine.Close(ctx)

	for _, testcase := range []struct {
		name       string
		parsedName map[string]string
		expected   string
	}{
		{
			name: "no scheme",
			parsedName: map[string]string{
				"path": ":",
			},
			expected: "parse :: missing protocol scheme",
		},
	} {
		t.Run(testcase.name, func(t *testing.T) {
			request, err := engine.(*Engine).getPreFetch(testcase.parsedName)
			if err == nil {
				t.Fatalf("returned %s and did not raise the expected error", request.URL)
			}
			assert.Regexp(t, testcase.expected, err.Error())
		})
	}
}

func TestGetPostFetchGood(t *testing.T) {
	ctx := context.Background()
	config := map[string]string{
		"uri": "https://example.com/index",
	}

	uri, err := url.Parse(config["uri"])
	if err != nil {
		t.Fatal(err)
	}

	request := &http.Request{
		URL: uri,
		Header: map[string][]string{
			"Accept": {"application/vnd.oci.image.index.v1+json"},
		},
	}

	engine, err := New(ctx, uri, config)
	if err != nil {
		t.Fatal(err)
	}
	defer engine.Close(ctx)

	for _, testcase := range []struct {
		label    string
		name     string
		response *v1new.Index
		expected []v1new.Descriptor
	}{
		{
			label: "empty fragment returns all entries",
			name:  "example.com/a",
			response: &v1new.Index{
				Manifests: []v1new.Descriptor{
					{
						Descriptor: v1.Descriptor{
							Size: 1,
						},
					},
					{
						Descriptor: v1.Descriptor{
							Size: 2,
							Annotations: map[string]string{
								"org.opencontainers.image.ref.name": "1.0",
							},
						},
					},
				},
			},
			expected: []v1new.Descriptor{
				{
					Descriptor: v1.Descriptor{
						Size: 1,
					},
				},
				{
					Descriptor: v1.Descriptor{
						Size: 2,
						Annotations: map[string]string{
							"org.opencontainers.image.ref.name": "1.0",
						},
					},
				},
			},
		},
		{
			label: "nonempty fragment returns only matching entries",
			name:  "example.com/a#1.0",
			response: &v1new.Index{
				Manifests: []v1new.Descriptor{
					{
						Descriptor: v1.Descriptor{
							Size: 1,
						},
					},
					{
						Descriptor: v1.Descriptor{
							Size: 2,
							Annotations: map[string]string{
								"org.opencontainers.image.ref.name": "1.0",
							},
						},
					},
				},
			},
			expected: []v1new.Descriptor{
				{
					Descriptor: v1.Descriptor{
						Size: 2,
						Annotations: map[string]string{
							"org.opencontainers.image.ref.name": "1.0",
						},
					},
				},
			},
		},
		{
			label: "unmatched fragment returns no entries",
			name:  "example.com/a#2.0",
			response: &v1new.Index{
				Manifests: []v1new.Descriptor{
					{
						Descriptor: v1.Descriptor{
							Size: 1,
						},
					},
					{
						Descriptor: v1.Descriptor{
							Size: 2,
							Annotations: map[string]string{
								"org.opencontainers.image.ref.name": "1.0",
							},
						},
					},
				},
			},
			expected: []v1new.Descriptor{},
		},
	} {
		t.Run(testcase.label, func(t *testing.T) {
			parsedName, err := hostbasedimagenames.Parse(testcase.name)
			if err != nil {
				t.Fatal(err)
			}

			bodyBytes, err := json.Marshal(testcase.response)
			if err != nil {
				t.Fatal(err)
			}

			response := &http.Response{
				Request: request,
				Header: map[string][]string{
					"Content-Type": {"application/vnd.oci.image.index.v1+json; charset=utf-8"},
				},
				Body: ioutil.NopCloser(bytes.NewReader(bodyBytes)),
			}

			roots, err := engine.(*Engine).getPostFetch(response, parsedName)
			if err != nil {
				t.Fatal(err)
			}

			expected := make([]refengine.MerkleRoot, len(testcase.expected))
			for i, descriptor := range testcase.expected {
				expected[i].MediaType = `application/vnd.oci.descriptor.v1+json`
				expected[i].Root = descriptor
				expected[i].URI = uri
			}

			assert.Equal(t, expected, roots)
		})
	}
}

func TestGetPostFetchBad(t *testing.T) {
	ctx := context.Background()
	config := map[string]string{
		"uri": "https://example.com/index",
	}

	engine, err := New(ctx, nil, config)
	if err != nil {
		t.Fatal(err)
	}
	defer engine.Close(ctx)

	parsedName, err := hostbasedimagenames.Parse("example.com/a")
	if err != nil {
		t.Fatal(err)
	}

	uri, err := url.Parse(config["uri"])
	if err != nil {
		t.Fatal(err)
	}
	request := &http.Request{
		URL: uri,
		Header: map[string][]string{
			"Accept": {"application/vnd.oci.image.index.v1+json"},
		},
	}

	for _, testcase := range []struct {
		label     string
		mediaType string
		body      string
		expected  string
	}{
		{
			label:     "invalid media type",
			mediaType: "a/b/c",
			body:      "",
			expected:  `mime: unexpected content after media subtype`,
		},
		{
			label:     "unexpected media type",
			mediaType: "application/octet-stream",
			body:      "",
			expected:  `requested application/vnd.oci.image.index.v1\+json from https://example.com/index but got application/octet-stream`,
		},
		{
			label:     "index is not a JSON object",
			mediaType: "application/vnd.oci.image.index.v1+json",
			body:      "[]",
			expected:  "json: cannot unmarshal array into Go value of type v1.Index",
		},
		{
			label:     "manifests is not a JSON array",
			mediaType: "application/vnd.oci.image.index.v1+json",
			body:      `{"manifests": {}}`,
			expected:  `json: cannot unmarshal object into Go .* of type \[\]v1.Descriptor`,
		},
		{
			label:     "manifests contains a non-object",
			mediaType: "application/vnd.oci.image.index.v1+json",
			body:      `{"manifests": [1]}`,
			expected:  `json: cannot unmarshal number into Go .* of type v1.Descriptor`,
		},
		{
			label:     "at least one manifests[].annotations is not a JSON object",
			mediaType: "application/vnd.oci.image.index.v1+json",
			body:      `{"manifests": [{"annotations": 1}]}`,
			expected:  `json: cannot unmarshal number into Go .* of type map\[string\]string`,
		},
	} {
		t.Run(testcase.label, func(t *testing.T) {
			response := &http.Response{
				Request: request,
				Header: map[string][]string{
					"Content-Type": {fmt.Sprintf("%s; charset=utf-8", testcase.mediaType)},
				},
				Body: ioutil.NopCloser(strings.NewReader(testcase.body)),
			}

			roots, err := engine.(*Engine).getPostFetch(response, parsedName)
			if err == nil {
				t.Fatalf("returned %v and did not raise the expected error", roots)
			}

			assert.Regexp(t, testcase.expected, err.Error())
		})
	}
}
