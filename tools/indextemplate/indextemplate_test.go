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
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	v1new "github.com/xiekeyang/oci-discovery/tools/newimagespec"
	"golang.org/x/net/context"
)

func TestResolveURI(t *testing.T) {
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

			uri, err := engine.(*Engine).resolveURI(parsedName)
			if err != nil {
				t.Fatal(err)
			}

			assert.Equal(t, uri.String(), testcase.expected)
		})
	}
}

func TestHandleIndexGood(t *testing.T) {
	ctx := context.Background()
	config := map[string]string{
		"uri": "https://example.com/index",
	}

	engine, err := New(ctx, nil, config)
	if err != nil {
		t.Fatal(err)
	}

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
				Body: ioutil.NopCloser(bytes.NewReader(bodyBytes)),
			}

			descriptors, err := engine.(*Engine).handleIndex(response, parsedName)
			if err != nil {
				t.Fatal(err)
			}

			assert.Equal(t, descriptors, testcase.expected)
		})
	}
}

func TestHandleIndexBad(t *testing.T) {
	ctx := context.Background()
	config := map[string]string{
		"uri": "https://example.com/index",
	}

	engine, err := New(ctx, nil, config)
	if err != nil {
		t.Fatal(err)
	}

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
	}

	for _, testcase := range []struct {
		label    string
		response string
		expected string
	}{
		{
			label:    "index is not a JSON object",
			response: "[]",
			expected: "json: cannot unmarshal array into Go value of type v1.Index",
		},
		{
			label:    "manifests is not a JSON array",
			response: `{"manifests": {}}`,
			expected: "json: cannot unmarshal object into Go value of type []v1.Descriptor",
		},
		{
			label:    "manifests contains a non-object",
			response: `{"manifests": [1]}`,
			expected: "json: cannot unmarshal number into Go value of type v1.Descriptor",
		},
		{
			label:    "at least one manifests[].annotations is not a JSON object",
			response: `{"manifests": [{"annotations": 1}]}`,
			expected: "json: cannot unmarshal number into Go value of type map[string]string",
		},
	} {
		t.Run(testcase.label, func(t *testing.T) {
			response := &http.Response{
				Request: request,
				Body:    ioutil.NopCloser(strings.NewReader(testcase.response)),
			}

			descriptors, err := engine.(*Engine).handleIndex(response, parsedName)
			if err == nil {
				t.Fatalf("returned %v and did not raise the expected error", descriptors)
			}

			assert.Equal(t, err.Error(), testcase.expected)
		})
	}
}
