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

package xdg

import (
	"sort"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSort(t *testing.T) {
	for _, testcase := range []struct {
		name     string
		values   []string
		expected []string
	}{
		{
			name:     "empty array",
			values:   nil,
			expected: nil,
		},
		{
			name:     "entries of different lengths",
			values:   []string{"a", "abc", "bc"},
			expected: []string{"abc", "bc", "a"},
		},
		{
			name:     "entries with the same length",
			values:   []string{"b", "a", "bc"},
			expected: []string{"bc", "a", "b"},
		},
	} {
		t.Run(testcase.name, func(t *testing.T) {
			sort.Sort(stringLengthSort(testcase.values))
			assert.Equal(t, testcase.expected, testcase.values)
		})
	}
}
