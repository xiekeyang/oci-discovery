package hostbasedimagenames

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseGood(t *testing.T) {
	for _, testcase := range []struct {
		Name     string
		Expected map[string]string
	}{
		{
			Name: "example.com/a",
			Expected: map[string]string{
				"name":     "example.com/a",
				"host":     "example.com",
				"path":     "a",
				"fragment": "",
			},
		},
		{
			Name: "example.com/a/",
			Expected: map[string]string{
				"name":     "example.com/a/",
				"host":     "example.com",
				"path":     "a/",
				"fragment": "",
			},
		},
		{
			Name: "example.com/a/b",
			Expected: map[string]string{
				"name":     "example.com/a/b",
				"host":     "example.com",
				"path":     "a/b",
				"fragment": "",
			},
		},
		{
			Name: "example.com/a/b#c",
			Expected: map[string]string{
				"name":     "example.com/a/b#c",
				"host":     "example.com",
				"path":     "a/b",
				"fragment": "c",
			},
		},
		{
			Name: "localhost/a",
			Expected: map[string]string{
				"name":     "localhost/a",
				"host":     "localhost",
				"path":     "a",
				"fragment": "",
			},
		},
		{
			Name: "127.0.0.1/a",
			Expected: map[string]string{
				"name":     "127.0.0.1/a",
				"host":     "127.0.0.1",
				"path":     "a",
				"fragment": "",
			},
		},
		{
			Name: "[::1]/a",
			Expected: map[string]string{
				"name":     "[::1]/a",
				"host":     "[::1]",
				"path":     "a",
				"fragment": "",
			},
		},
	} {
		t.Run(testcase.Name, func(t *testing.T) {
			parsed, err := Parse(testcase.Name)
			if err != nil {
				t.Fatal(err)
			}
			assert.Equal(t, parsed, testcase.Expected)
		})
	}
}

func TestParseBad(t *testing.T) {
	for _, name := range []string{
		"example.com",
		"/",
		"example.com/",
		"example.com/#",
		"example.com:80/a",
		"[::1]:80/a",
	} {
		t.Run(name, func(t *testing.T) {
			parsed, err := Parse(name)
			if err == nil {
				t.Fatalf("expected an error, but got %v", parsed)
			}
		})
	}
}
