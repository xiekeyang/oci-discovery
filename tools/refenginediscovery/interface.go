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
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"golang.org/x/net/context"
)

// Reference holds a single resolved ref-engine object.
type Reference struct {
	// Config holds a single resolved ref-engine config.
	Config engine.Reference

	// CASEngines holds the ref-engines object's CAS-engine suggestions,
	// if any.
	CASEngines []engine.Reference
}

// RefEngineCallback templates a callback for use in RefEngines.
type RefEngineCallback func(ctx context.Context, refEngine Reference) (err error)

// Engine represents a ref-engine discovery engine.
type Engine interface {

	// RefEngines calculates ref engines using Ref-Engine Discovery and
	// calls refEngineCallback on each one.  Discover returns any errors
	// returned by refEngineCallback and aborts further iteration.
	RefEngines(ctx context.Context, name string, refEngineCallback RefEngineCallback) (err error)

	// Close releases resources held by the engine.  Subsequent engine
	// method calls will fail.
	Close(ctx context.Context) (err error)
}
