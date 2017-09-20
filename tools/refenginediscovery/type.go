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

package refenginediscovery

import (
	"net/url"

	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"golang.org/x/net/context"
)

// Config holds application/vnd.oci.ref-engines.v1+json data.
type Config struct {

	// RefEngines is an array of ref-engine configurations.
	RefEngines []engine.Config `json:"refEngines,omitempty"`

	// CASEngines is an array of CAS-engine configurations.
	CASEngines []engine.Config `json:"casEngines,omitempty"`
}

// Base holds a resolved ref-engines object.
type Base struct {

	// Config holds the application/vnd.oci.ref-engines.v1+json data.
	Config Config

	// URI is the source, if any, from which Config was retrieved.  It
	// can be used to expand any relative reference contained within
	// Config.
	URI *url.URL
}

// ResolvedCASEngine holds a CAS-engine configuration and the URI
// from which it was retrieved.
type ResolvedCASEngines struct {

	// Config the CAS-engine configuration.
	Config engine.Config

	// URI is the source, if any, from which Config was retrieved.  It
	// can be used to expand any relative reference contained within
	// Config.
	URI *url.URL
}

// RefEngineCallback templates a callback for use in RefEngines.
type RefEngineCallback func(ctx context.Context, refEngine refengine.Engine, casEngines []ResolvedCASEngines) (err error)
