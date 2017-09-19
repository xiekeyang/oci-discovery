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

package v1

import (
	"github.com/opencontainers/image-spec/specs-go/v1"
	"github.com/xiekeyang/oci-discovery/tools/engine"
)

type Descriptor struct {
	v1.Descriptor

	// CASEngines specifies a list of CAS engines from which this object
	// and its dependencies MAY be downloaded.
	CASEngines []engine.Config `json:"casEngines,omitempty"`
}

type Index struct {
	// Manifests references platform specific manifests.
	Manifests []Descriptor `json:"manifests"`
}
