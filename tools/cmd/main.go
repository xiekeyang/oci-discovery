package main

import (
	"os"

	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"
	"github.com/xiekeyang/oci-discovery/tools/discovery"
)

var discoveryCommand = cli.Command{
	Name:   "discovery",
	Usage:  "Resolve image names via OCI Ref-engine Discovery.",
	Action: discovery.DiscoveryHandler,
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
}

func main() {
	app := cli.NewApp()
	app.Name = "oci-discovery-tool"
	app.Usage = "OCI (Open Container Initiative) image discovery tools"
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
		discoveryCommand,
	}

	if err := app.Run(os.Args); err != nil {
		logrus.Fatal(err)
	}
}
