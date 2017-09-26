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
	"net/url"

	"github.com/xiekeyang/oci-discovery/tools/engine"
)

// Engines holds application/vnd.oci.ref-engines.v1+json data.
type Engines struct {

	// RefEngines is an array of ref-engine configurations.
	RefEngines []engine.Config `json:"refEngines,omitempty"`

	// CASEngines is an array of CAS-engine configurations.
	CASEngines []engine.Config `json:"casEngines,omitempty"`
}

// Reference holds resolved Engines data.
type Reference struct {

	// Engines holds the resolved Engines declaration.
	Engines Engines

	// URI is the source, if any, from which Engines was retrieved.  It
	// can be used to expand any relative reference contained within
	// Engines.
	URI *url.URL
}
