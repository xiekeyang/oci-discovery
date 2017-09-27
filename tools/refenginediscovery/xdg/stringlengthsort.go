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

// stringLengthSort implements sort.Interface to order an array of
// strings by decreasing length.  Length ties are broken by byte
// order.
type stringLengthSort []string

// Len is the number of elements in the collection.
func (s stringLengthSort) Len() int {
	return len(s)
}

// Less reports whether the element with index i should sort before
// the element with index j.
func (s stringLengthSort) Less(i, j int) bool {
	leni := len(s[i])
	lenj := len(s[j])
	if leni > lenj {
		return true
	} else if leni == lenj {
		return s[i] < s[j]
	}
	return false
}

// Swap swaps the elements with indexes i and j.
func (s stringLengthSort) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
