// Package hostbasedimagenames implements Host Based Image Names v1.
package hostbasedimagenames

import (
	"fmt"
	"regexp"
)

var (
	// The normative ABNF is in host-based-image-names.md referencing
	// rules from https://tools.ietf.org/html/rfc3986#appendix-A.
	unreservedNoHyphen = `a-zA-Z0-9._~`
	subDelims          = `!$&'()*+,;=`
	pchar              = unreservedNoHyphen + `%` + subDelims + `:@` + `-`
	decOctet           = `([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[05])`
	hexDig             = `[0-9a-fA-F]`
	h16                = hexDig + `{1,4}`
	ipv4address        = decOctet + `(\.` + decOctet + `){3}`
	ls32               = `((` + h16 + `:` + h16 + `)|` + ipv4address + `)`
	ipv6address        = (`(` +
		`((` + h16 + `:){6}` + ls32 + `)|` +
		`(::(` + h16 + `:){5}` + ls32 + `)|` +
		`(` + h16 + `?::(` + h16 + `:){4}` + ls32 + `)|` +
		`(((` + h16 + `:){,1}` + h16 + `)?::(` + h16 + `:){3}` + ls32 + `)|` +
		`(((` + h16 + `:){,2}` + h16 + `)?::(` + h16 + `:){2}` + ls32 + `)|` +
		`(((` + h16 + `:){,3}` + h16 + `)?::` + h16 + `:` + ls32 + `)|` +
		`(((` + h16 + `:){,4}` + h16 + `)?::` + ls32 + `)|` +
		`(((` + h16 + `:){,5}` + h16 + `)?::` + h16 + `)|` +
		`(((` + h16 + `:){,6}` + h16 + `)?::)` +
		`)`)
	ipvFuture = (`v` + hexDig + `+\.` +
		`([` + unreservedNoHyphen + subDelims + `:` + `-` + `])+`)
	ipLiteral          = `\[(` + ipv6address + `|` + ipvFuture + `)]`
	regName            = `[` + unreservedNoHyphen + `%` + subDelims + `-]*`
	host               = `(` + ipLiteral + `|` + ipv4address + `|` + regName + `)`
	path               = `[` + pchar + `]+(/[` + pchar + `]*)*`
	fragment           = `[/?` + pchar + `]*`
	hostBasedImageName = regexp.MustCompile(
		`^(?P<host>` + host + `)/(?P<path>` + path + `)(#(?P<fragment>` + fragment + `))?$`)
)

// Parse takes a host-based image name and returns a map[string]string
// with host, path, and fragment keys, and values extracted from the
// image name.
func Parse(name string) (matches map[string]string, err error) {
	matches = make(map[string]string)

	submatches := hostBasedImageName.FindStringSubmatch(name)
	for i, submatchName := range hostBasedImageName.SubexpNames() {
		if submatchName == "" {
			continue
		}
		if i > len(submatches) {
			return nil, fmt.Errorf("%q does not match the host-based-image-name pattern", name)
		}
		matches[submatchName] = submatches[i]
	}

	_, ok := matches["fragment"]
	if !ok {
		matches["fragment"] = ""
	}

	return matches, nil
}
