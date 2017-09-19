package discovery

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"

	"github.com/opencontainers/image-spec/specs-go/v1"
	"github.com/sirupsen/logrus"
	"github.com/urfave/cli"
	"github.com/xiekeyang/oci-discovery/tools/hostbasedimagenames"
	"github.com/xiekeyang/oci-discovery/tools/object"
)

var (
	defaultTrans = &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
)

func DiscoveryHandler(context *cli.Context) error {
	var (
		name  = context.Args()[0]
		roots []v1.Descriptor
	)

	parsedName, err := hostbasedimagenames.Parse(name)
	if err != nil {
		return err
	}

	engines, err := refEnginesFetching(parsedName)
	if err != nil {
		return err
	}

	for _, engine := range engines.RefEngines {
		var ur urlResolver = urlResolver(engine.Uri)
		u, err := ur.resolve(StringStringToStringInterface(parsedName))
		if err != nil {
			return err
		}

		index, err := ociIndexFetching(u)
		if err != nil {
			return err
		}

		if fragment, ok := parsedName["fragment"]; ok && len(fragment) > 0 {
			for _, manifest := range index.Manifests {
				if fragment == manifest.Annotations[`org.opencontainers.image.ref.name`] {
					roots = append(roots, manifest)
				}
			}
		} else {
			roots = append(roots, index.Manifests...)
		}
	}

	return stdWrite(roots)
}

func refEnginesFetching(parsedName map[string]string) (*object.RefEngines, error) {
	u, err := templateRefEngines.resolve(StringStringToStringInterface(parsedName))
	if err != nil {
		return nil, err
	}

	client := &http.Client{Transport: defaultTrans}

	req, err := http.NewRequest("GET", u.String(), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", `application/vnd.oci.ref-engines.v1+json`)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("ref engine fetching error, status code = %d", resp.StatusCode)
	}

	var engines object.RefEngines
	if err := json.NewDecoder(resp.Body).Decode(&engines); err != nil {
		logrus.Errorf("ref engines object decoded failed: %s", err)
		return nil, err
	}

	return &engines, nil
}

func ociIndexFetching(u *url.URL) (*v1.Index, error) {
	var index *v1.Index

	client := &http.Client{Transport: defaultTrans}

	req, err := http.NewRequest("GET", u.String(), nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Accept", `application/vnd.oci.image.index.v1+json`)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if err := json.NewDecoder(resp.Body).Decode(&index); err != nil {
		logrus.Errorf("index decoded failed: %s", err)
		return nil, err
	}

	return index, nil
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
