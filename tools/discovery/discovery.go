package discovery

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"mime"
	"net/http"
	"net/url"
	"os"

	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"
	"github.com/xiekeyang/oci-discovery/tools/engine"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	v1 "github.com/xiekeyang/oci-discovery/tools/newimagespec"
	"github.com/xiekeyang/oci-discovery/tools/refengine"
	"github.com/xiekeyang/oci-discovery/tools/util"
	"golang.org/x/net/context"
)

var (
	defaultTrans = &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
)

type RefEngines struct {
	RefEngines []engine.Config `json:"refEngines,omitempty"`
	CASEngines []engine.Config `json:"casEngines,omitempty"`
}

func DiscoveryHandler(cliContext *cli.Context) error {
	var (
		ctx   = context.Background()
		name  = cliContext.Args()[0]
		roots = []v1.Descriptor{}
	)

	parsedName, err := hostbasedimagenames.Parse(name)
	if err != nil {
		return err
	}

	uri, engines, err := refEnginesFetching(parsedName)
	if err != nil {
		return err
	}

	for _, config := range engines {
		constructor, ok := refengine.Constructors[config.Protocol]
		if !ok {
			logrus.Debugf("unsupported ref-engine protocol %q (%v)", config.Protocol, refengine.Constructors)
			continue
		}
		engine, err := constructor(ctx, uri, config.Data)
		if err != nil {
			logrus.Warnf("failed to initialize %s ref-engine with %v: %s", config.Protocol, config.Data, err)
			continue
		}
		roots, err = engine.Get(ctx, name)
		if err != nil {
			logrus.Warnf("failed to resolve %q with %s ref-engine (%v): %s", name, config.Protocol, config.Data, err)
			continue
		}
		return stdWrite(roots)
	}

	return stdWrite(roots)
}

func refEnginesFetching(parsedName map[string]string) (uri *url.URL, engines []engine.Config, err error) {
	uri, err = templateRefEngines.resolve(util.StringStringToStringInterface(parsedName))
	if err != nil {
		return nil, nil, err
	}

	client := &http.Client{Transport: defaultTrans}

	logrus.Debugf("requesting application/vnd.oci.ref-engines.v1+json from %s", uri)
	resp, err := client.Get(uri.String())
	if err != nil {
		return uri, nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return uri, nil, fmt.Errorf("ref engine fetching error, status code = %d", resp.StatusCode)
	}

	mediatype, _, err := mime.ParseMediaType(resp.Header.Get(`Content-Type`))
	if err != nil {
		return uri, nil, err
	}

	if mediatype != `application/vnd.oci.ref-engines.v1+json` {
		return uri, nil, fmt.Errorf("Unknown Content-Type: %s", mediatype)
	}

	var refEngines RefEngines
	if err := json.NewDecoder(resp.Body).Decode(&refEngines); err != nil {
		logrus.Errorf("ref engines object decoded failed: %s", err)
		return uri, nil, err
	}

	return uri, refEngines.RefEngines, nil
}

func stdWrite(v interface{}) error {
	var out bytes.Buffer

	b, err := json.Marshal(v)
	if err != nil {
		return err
	}

	err = json.Indent(&out, b, "", "\t")
	if err != nil {
		return err
	}

	_, err = out.WriteTo(os.Stdout)
	if err != nil {
		return err
	}

	return nil
}
