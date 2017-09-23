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

package engine

import (
	"encoding/json"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestReferenceGood(t *testing.T) {
	for _, testcase := range []struct {
		JSON     string
		Expected Reference
	}{
		{
			JSON: `{"config":{"protocol":"oci-image-template-v1","uri":"index.json"}}`,
			Expected: Reference{
				Config: Config{
					Protocol: "oci-image-template-v1",
					Data: map[string]interface{}{
						"uri": "index.json",
					},
				},
				URI: nil,
			},
		},
		{
			JSON: `{"config":{"protocol":"oci-image-template-v1","uri":"index.json"},"uri":"https://example.com"}`,
			Expected: Reference{
				Config: Config{
					Protocol: "oci-image-template-v1",
					Data: map[string]interface{}{
						"uri": "index.json",
					},
				},
				URI: &url.URL{
					Scheme: "https",
					Host:   "example.com",
				},
			},
		},
	} {
		t.Run(testcase.JSON, func(t *testing.T) {
			reference := Reference{
				Config: Config{
					Protocol: "initial value",
					Data: map[string]interface{}{
						"initial": "value",
					},
				},
				URI: &url.URL{
					Scheme: "https",
					Host:   "initial.value.example.com",
				},
			}
			json.Unmarshal([]byte(testcase.JSON), &reference)
			assert.Equal(t, testcase.Expected, reference)
			marshaled, err := json.Marshal(reference)
			if err != nil {
				t.Fatal(err)
			}
			assert.Equal(t, testcase.JSON, string(marshaled))
		})
	}
}
