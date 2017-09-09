# Host-Based Image Names

This is version 1 of this specification.

The [X.509 Public Key Infrastructure][X.509] provides a well-established mechanism for trusted namespacing of [domain names][rfc5890].
Protocols interested in leveraging that infrastructure need to be able to extract domain names from image names.
This specification provides one approach for that extraction.

This specification defines image names compatible with host names using the following [ABNF][]:

```ABNF
host-based-image-name = host "/" path-rootless [ "#" fragment ]
```

where:

* `host` is defined in [RFC 3986 section 3.2.2][rfc3986-s3.2.2].
    While IP addresses are valid host names, X.509 certificates usually assert ownership of one or more domain names and do not mention IP addresses.
    Host-based image names SHOULD use host names that conform [RFC 1034's preferred name syntax][rfc1034-s3.5] as modified by [RFC 1123 section 2.1][rfc1123-s2.1].
* `path-rootless` is defined in [RFC 3986 section 3.3][rfc3986-s3.3].
* `fragment` is defined in [RFC 3986 section 3.5][rfc3986-s3.5].

Implementations MAY accept other names, for example, by creating a default `host` for names that match `segment-nz` (defined in [RFC 3986 section 3.3][rfc3986-s3.3]).

Names which are not supported for `host-based-image-name` will not be able to use protocols that rely on this rule, although they may use other protocols.

[ABNF]: https://tools.ietf.org/html/rfc5234
[rfc1034-s3.5]: https://tools.ietf.org/html/rfc1034#section-3.5
[rfc1123-s2.1]: https://tools.ietf.org/html/rfc1123#section-2
[rfc3986-s3.2.2]: https://tools.ietf.org/html/rfc3986#section-3.2.2
[rfc3986-s3.3]: https://tools.ietf.org/html/rfc3986#section-3.3
[rfc3986-s3.5]: https://tools.ietf.org/html/rfc3986#section-3.5
[rfc5890]: https://tools.ietf.org/html/rfc5890
[X.509]: https://tools.ietf.org/html/rfc5280
