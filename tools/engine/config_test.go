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
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConfigGood(t *testing.T) {
	for _, testcase := range []struct {
		JSON     string
		Expected Config
	}{
		{
			JSON: `{"protocol":"oci-image-template-v1","uri":"index.json"}`,
			Expected: Config{
				Protocol: "oci-image-template-v1",
				Data: map[string]interface{}{
					"uri": "index.json",
				},
			},
		},
		{
			JSON: `{"protocol":"nested-array","x-array":[1.2,3.4]}`,
			Expected: Config{
				Protocol: "nested-array",
				Data: map[string]interface{}{
					"x-array": []interface{}{1.2, 3.4},
				},
			},
		},
	} {
		t.Run(testcase.JSON, func(t *testing.T) {
			var config Config
			json.Unmarshal([]byte(testcase.JSON), &config)
			assert.Equal(t, config, testcase.Expected)
			marshaled, err := json.Marshal(config)
			if err != nil {
				t.Fatal(err)
			}
			assert.Equal(t, string(marshaled), testcase.JSON)
		})
	}
}
