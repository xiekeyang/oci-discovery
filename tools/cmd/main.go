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
	"os"

	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"

	_ "github.com/xiekeyang/oci-discovery/tools/refengine/indextemplate"
)

func main() {
	app := cli.NewApp()
	app.Name = "oci-discovery-tool"
	app.Usage = "OCI (Open Container Initiative) image discovery tools."
	app.Flags = []cli.Flag{
		cli.BoolFlag{
			Name:  "debug",
			Usage: "enable debug output",
		},
	}
	app.Before = func(c *cli.Context) error {
		if c.GlobalBool("debug") {
			logrus.SetLevel(logrus.DebugLevel)
		}
		return nil
	}
	app.Commands = []cli.Command{
		resolveCommand,
	}

	if err := app.Run(os.Args); err != nil {
		logrus.Fatal(err)
	}
}
