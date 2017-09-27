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
	"os"

	"github.com/BurntSushi/xdg"
	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery"
	"github.com/xiekeyang/oci-discovery/tools/refenginediscovery/wellknownuri"
	xdgeng "github.com/xiekeyang/oci-discovery/tools/refenginediscovery/xdg"
	"golang.org/x/net/context"
)

type resolvedName struct {
	refengine.MerkleRoot

	// CASEngines holds the ref-engines object's CAS-engine suggestions,
	// if any.
	CASEngines []engine.Reference
}

// Add casEngines as a sibling of the MerkleRoot properties.
func (resolved resolvedName) MarshalJSON() ([]byte, error) {
	b, err := json.Marshal(resolved.MerkleRoot)
	if err != nil {
		return nil, err
	}

	var data map[string]interface{}
	err = json.Unmarshal(b, &data)
	if err != nil {
		return nil, err
	}

	if resolved.CASEngines != nil {
		data["casEngines"] = resolved.CASEngines
	}
	return json.Marshal(data)
}

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
		resolvedNames := map[string][]resolvedName{}

		protocols := []string{}
		if c.IsSet("protocol") {
			protocols = append(protocols, c.String("protocol"))
		}

		engines := []refenginediscovery.Engine{}

		eng, err := xdgeng.New(ctx, xdg.Paths{
			XDGSuffix: "oci-discovery",
		})
		if err != nil {
			logrus.Warn(err)
		} else {
			defer eng.Close(ctx)
			engines = append(engines, eng)
		}

		eng, err = wellknownuri.New(ctx, protocols)
		if err != nil {
			logrus.Warn(err)
		} else {
			defer eng.Close(ctx)
			engines = append(engines, eng)
		}

		for _, name := range c.Args() {
			err = refenginediscovery.ResolveName(
				ctx,
				engines,
				name,
				func(ctx context.Context, root refengine.MerkleRoot, casEngines []engine.Reference) (err error) {
					return resolvedNameCallback(ctx, root, casEngines, resolvedNames, name)
				},
			)
			if err != nil {
				logrus.Warn(err)
			}
		}

		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "\t")
		return encoder.Encode(resolvedNames)
	},
}

func resolvedNameCallback(ctx context.Context, root refengine.MerkleRoot, casEngines []engine.Reference, resolvedNames map[string][]resolvedName, name string) (err error) {
	_, ok := resolvedNames[name]
	if !ok {
		resolvedNames[name] = []resolvedName{}
	}
	resolvedNames[name] = append(resolvedNames[name], resolvedName{
		MerkleRoot: root,
		CASEngines: casEngines,
	})
	return nil
}
