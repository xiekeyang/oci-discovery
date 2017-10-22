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
	"fmt"
	"net/url"
	"testing"

	"github.com/BurntSushi/xdg"
	"github.com/stretchr/testify/assert"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery"
	"golang.org/x/net/context"
)

func TestNewGood(t *testing.T) {
	ctx := context.Background()
	engine, err := New(ctx, xdg.Paths{})
	if err != nil {
		t.Fatal(err)
	}

	err = engine.Close(ctx)
	if err != nil {
		t.Fatal(err)
	}
}

func TestRefEnginesGood(t *testing.T) {
	ctx := context.Background()
	for _, testcase := range []struct {
		label            string
		regexpRefEngines map[string]refenginediscovery.RefEnginesReference
		name             string
		expected         []refenginediscovery.RefEngineReference
	}{
		{
			label:            "nil regexpRefEngines",
			regexpRefEngines: nil,
			name:             "example",
			expected:         []refenginediscovery.RefEngineReference{},
		},
		{
			label: "no matching regexps",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
			},
			name:     "example",
			expected: []refenginediscovery.RefEngineReference{},
		},
		{
			label: "single matching regexp with one ref-engine config",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
			},
			name: "app",
			expected: []refenginediscovery.RefEngineReference{
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
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
			},
		},
		{
			label: "single matching regexp with one ref-engine and one CAS-engine config",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
						CASEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
			},
			name: "app",
			expected: []refenginediscovery.RefEngineReference{
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
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
					CASEngines: []engine.Reference{
						engine.Reference{
							Config: engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
							URI: &url.URL{
								Scheme: "https",
								Host:   "example.com",
							},
						},
					},
				},
			},
		},
		{
			label: "two matching regexps of different length",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
						CASEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
				"^ap.*$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "/other-index",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "file",
						Path:   "/example",
					},
				},
			},
			name: "app",
			expected: []refenginediscovery.RefEngineReference{
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
							Protocol: "oci-image-template-v1",
							Data: map[string]interface{}{
								"uri": "/other-index",
							},
						},
						URI: &url.URL{
							Scheme: "file",
							Path:   "/example",
						},
					},
				},
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
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
					CASEngines: []engine.Reference{
						engine.Reference{
							Config: engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
							URI: &url.URL{
								Scheme: "https",
								Host:   "example.com",
							},
						},
					},
				},
			},
		},
		{
			label: "two matching regexps of same length",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"^ap.$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
						CASEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "/other-index",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "file",
						Path:   "/example",
					},
				},
			},
			name: "app",
			expected: []refenginediscovery.RefEngineReference{
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
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
					CASEngines: []engine.Reference{
						engine.Reference{
							Config: engine.Config{
								Protocol: "oci-cas-template-v1",
								Data: map[string]interface{}{
									"uri": "/{algorithm}/{encoded}",
								},
							},
							URI: &url.URL{
								Scheme: "https",
								Host:   "example.com",
							},
						},
					},
				},
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
							Protocol: "oci-image-template-v1",
							Data: map[string]interface{}{
								"uri": "/other-index",
							},
						},
						URI: &url.URL{
							Scheme: "file",
							Path:   "/example",
						},
					},
				},
			},
		},
		{
			label: "invalid regexp ignored",
			regexpRefEngines: map[string]refenginediscovery.RefEnginesReference{
				"[": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
				"^app$": refenginediscovery.RefEnginesReference{
					Engines: refenginediscovery.Engines{
						RefEngines: []engine.Config{
							engine.Config{
								Protocol: "oci-image-template-v1",
								Data: map[string]interface{}{
									"uri": "index.json",
								},
							},
						},
					},
					URI: &url.URL{
						Scheme: "https",
						Host:   "example.com",
					},
				},
			},
			name: "app",
			expected: []refenginediscovery.RefEngineReference{
				refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: engine.Config{
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
			},
		},
	} {
		t.Run(testcase.label, func(t *testing.T) {
			refEngines := []refenginediscovery.RefEngineReference{}
			err := RefEngines(ctx, testcase.regexpRefEngines, testcase.name, func(ctx context.Context, refEngine refenginediscovery.RefEngineReference) error {
				refEngines = append(refEngines, refEngine)
				return nil
			})
			if err != nil {
				t.Fatal(err)
			}

			assert.Equal(t, testcase.expected, refEngines)
		})
	}
}

func TestRefEnginesCallbackError(t *testing.T) {
	ctx := context.Background()
	regexpRefEngines := map[string]refenginediscovery.RefEnginesReference{
		"^app$": refenginediscovery.RefEnginesReference{
			Engines: refenginediscovery.Engines{
				RefEngines: []engine.Config{
					engine.Config{
						Protocol: "oci-image-template-v1",
						Data: map[string]interface{}{
							"uri": "index.json",
						},
					},
				},
			},
			URI: &url.URL{
				Scheme: "https",
				Host:   "example.com",
			},
		},
	}
	testError := fmt.Errorf("testing")
	err := RefEngines(ctx, regexpRefEngines, "app", func(ctx context.Context, refEngine refenginediscovery.RefEngineReference) error {
		return testError
	})
	assert.Equal(t, testError, err)
}
