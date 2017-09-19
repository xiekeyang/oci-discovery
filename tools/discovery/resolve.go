package discovery

import (
	"net/url"

	"github.com/jtacoma/uritemplates"
	"github.com/sirupsen/logrus"
)

const (
	templateRefEngines urlResolver = `https://{host}/.well-known/oci-host-ref-engines`
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

// FIXME: Can we do this just by casting?
func StringStringToStringInterface(input map[string]string) (output map[string]interface{}) {
	output = make(map[string]interface{})
	for key, value := range input {
		output[key] = value
	}
	return output
}
