package discovery

import (
	"fmt"
	"net/url"

	"github.com/jtacoma/uritemplates"
	"github.com/sirupsen/logrus"
)

const (
	templateRefEngines urlResolver = `{host}/.well-known/oci-host-ref-engines`
)

type urlResolver string

func (ur urlResolver) resolve(v map[string]interface{}) (*url.URL, error) {
	t, err := uritemplates.Parse(string(ur))
	if err != nil {
		return nil, err
	}

	rawurl, err := t.Expand(v)
	if err != nil {
		logrus.Errorf("name resolving failed: %s", err)
		return nil, err
	}

	u, err := url.Parse(rawurl)
	if err != nil {
		return nil, err
	}
	u.Scheme = "http"

	return u, nil
}

func paramsParser(name string) (map[string]interface{}, error) {
	var v = make(map[string]interface{})

	parsed := RegHostBasedImage.FindStringSubmatch(name)
	if len(parsed) != 3 && len(parsed) != 4 {
		return nil, fmt.Errorf("%s does not match the host-based-image-name pattern", name)
	}

	v["host"] = parsed[1]
	v["path"] = parsed[2]

	if len(parsed) == 4 {
		v["fragment"] = parsed[3]
	}

	return v, nil
}
