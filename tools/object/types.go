package object

import (
	"github.com/opencontainers/go-digest"
)

type RefEngine struct {
	Protocol string `json:"protocol,omitempty"`
	Uri      string `json:"uri,omitempty"`
}

type Manifest struct {
	Digest     digest.Digest `json:"digest"`
	CasEngines []RefEngine   `json:"casEngines,omitempty"`
}

type RefEngines struct {
	RefEngines []RefEngine `json:"refEngines,omitempty"`
}

type CasEngines struct {
	Manifests []Manifest `json:"manifests,omitempty"`
}
