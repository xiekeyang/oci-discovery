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
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"regexp"
	"sort"

	"github.com/BurntSushi/xdg"
	"github.com/sirupsen/logrus"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery"
	"golang.org/x/net/context"
)

// Engine implements the XDG Ref-Engine Discovery protocol.
type Engine struct {
	xdgPaths xdg.Paths
}

// New creates a new ref-engine-discovery instance.
func New(ctx context.Context, xdgPaths xdg.Paths) (engine refenginediscovery.Engine, err error) {
	return &Engine{
		xdgPaths: xdgPaths,
	}, nil
}

// RefEngines calculates ref engines using the XDG Ref-Engine
// Discovery Protocol and calls callback on each one.  This method
// includes local code for filesystem retrieval, but the logic for
// processing the retrieved data is in the RefEngines function for
// consumers that want to reuse it outside of an XDG Engine.
func (eng *Engine) RefEngines(ctx context.Context, name string, callback refenginediscovery.RefEngineReferenceCallback) (err error) {
	path, err := eng.xdgPaths.ConfigFile("ref-engine-discovery.json")
	if err != nil {
		logrus.Warn(err)
		return nil
	}
	// FIXME: iterate through lower-preference paths
	// https://github.com/BurntSushi/xdg/issues/3

	uriString := fmt.Sprintf("file://" + path) // FIXME: Convert Windows separators
	uri, err := url.Parse(uriString)
	if err != nil {
		logrus.Warn(err)
		return nil
	}

	logrus.Debugf("requesting application/vnd.oci.regexp-ref-engines.v1+json from %s", uri)
	file, err := os.Open(path)
	if err != nil {
		logrus.Warn(err)
		return nil
	}
	defer file.Close()

	var data map[string]refenginediscovery.Engines
	err = json.NewDecoder(file).Decode(&data)
	if err != nil {
		logrus.Warn(err)
		return nil
	}

	regexpRefEngines := map[string]refenginediscovery.RefEnginesReference{}
	for key, value := range data {
		regexpRefEngines[key] = refenginediscovery.RefEnginesReference{
			Engines: value,
			URI:     uri,
		}
	}

	return RefEngines(ctx, regexpRefEngines, name, callback)
}

// Close releases resources held by the engine.
func (eng *Engine) Close(ctx context.Context) (err error) {
	return nil
}

// RefEngines processes a regexp ref engines object, calling
// refEngineCallback for each ref-engine config matching name.
// RefEngines returns any errors returned by callback and aborts
// further iteration.  Other errors (e.g. in compiling a regexp)
// generate logged warnings but are otherwise ignored.
func RefEngines(ctx context.Context, regexpRefEngines map[string]refenginediscovery.RefEnginesReference, name string, callback refenginediscovery.RefEngineReferenceCallback) (err error) {
	patterns := []string{}
	for pattern := range regexpRefEngines {
		patterns = append(patterns, pattern)
	}
	sort.Sort(stringLengthSort(patterns))

	for _, pattern := range patterns {
		pat, err := regexp.Compile(pattern)
		if err != nil {
			logrus.Warn(err)
			continue
		}
		if pat.MatchString(name) {
			var casEngines []engine.Reference
			if regexpRefEngines[pattern].Engines.CASEngines != nil {
				casEngines = make([]engine.Reference, len(regexpRefEngines[pattern].Engines.CASEngines))
				for i, config := range regexpRefEngines[pattern].Engines.CASEngines {
					casEngines[i].Config = config
					casEngines[i].URI = regexpRefEngines[pattern].URI
				}
			}
			for _, config := range regexpRefEngines[pattern].Engines.RefEngines {
				ref := refenginediscovery.RefEngineReference{
					Config: engine.Reference{
						Config: config,
						URI:    regexpRefEngines[pattern].URI,
					},
					CASEngines: casEngines,
				}
				err = callback(ctx, ref)
				if err != nil {
					return err
				}
			}
		}
	}

	return nil
}
