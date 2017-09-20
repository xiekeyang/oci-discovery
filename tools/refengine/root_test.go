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

package refengine

import (
	"encoding/json"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMerkleRootGood(t *testing.T) {
	for _, testcase := range []struct {
		JSON     string
		Expected MerkleRoot
	}{
		{
			JSON: `{"root":"a"}`,
			Expected: MerkleRoot{
				Root: "a",
			},
		},
		{
			JSON: `{"mediaType":"text/plain"}`,
			Expected: MerkleRoot{
				MediaType: "text/plain",
			},
		},
		{
			JSON: `{"root":"a","uri":"https://example.com"}`,
			Expected: MerkleRoot{
				MediaType: "",
				Root:      "a",
				URI: &url.URL{
					Scheme: "https",
					Host:   "example.com",
				},
			},
		},
		{
			JSON: `{"root":[1.2,3.4],"uri":"https://example.com"}`,
			Expected: MerkleRoot{
				Root: []interface{}{1.2, 3.4},
				URI: &url.URL{
					Scheme: "https",
					Host:   "example.com",
				},
			},
		},
	} {
		t.Run(testcase.JSON, func(t *testing.T) {
			var root MerkleRoot
			json.Unmarshal([]byte(testcase.JSON), &root)
			assert.Equal(t, testcase.Expected, root)
			marshaled, err := json.Marshal(root)
			if err != nil {
				t.Fatal(err)
			}
			assert.Equal(t, testcase.JSON, string(marshaled))
		})
	}
}
