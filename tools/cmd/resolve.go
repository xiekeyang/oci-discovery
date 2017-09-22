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

package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery"
	"golang.org/x/net/context"
)

// resolved is a flag for breaking discovery iteration.
var resolved = fmt.Errorf("satisfactory resolution")

var resolveCommand = cli.Command{
	Name:  "resolve",
	Usage: "Resolve image names via OCI Ref-Engine Discovery.",
	Flags: []cli.Flag{
		cli.StringFlag{
			Name:  "protocol",
			Usage: "Protocol to use for ref-engine discovery",
		},
		cli.UintFlag{
			Name:  "port",
			Usage: "Port to use for ref-engine discovery",
		},
	},
	Action: func(c *cli.Context) error {
		ctx := context.Background()
		allRoots := map[string][]refengine.MerkleRoot{}

		protocols := []string{}
		if c.IsSet("protocol") {
			protocols = append(protocols, c.String("protocol"))
		}

		for _, name := range c.Args() {
			parsedName, err := hostbasedimagenames.Parse(name)
			if err != nil {
				logrus.Warn(err)
				continue
			}

			err = refenginediscovery.Discover(
				ctx, protocols, parsedName["host"],
				func(ctx context.Context, refEngine refengine.Engine, casEngines []refenginediscovery.ResolvedCASEngine) error {
					return resolveCallback(ctx, allRoots, refEngine, casEngines, name)
				})
			if err == resolved {
				continue
			} else if err != nil {
				logrus.Warn(err)
			}
		}

		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "\t")
		return encoder.Encode(allRoots)
	},
}

func resolveCallback(ctx context.Context, allRoots map[string][]refengine.MerkleRoot, refEngine refengine.Engine, casEngines []refenginediscovery.ResolvedCASEngine, name string) (err error) {
	roots, err := refEngine.Get(ctx, name)
	if err != nil {
		logrus.Warn(err)
		return nil
	}
	allRoots[name] = roots
	return resolved
}
