# OCI XDG Ref-Engine Discovery

This is version 0.1 of this specification.

To faciliate local control over image resolution, this specification defines a [ref-engine discovery](glossary.md#ref-engine-discovery) protocol which consumers and their local sysadmins MAY use to provide local [reference engine](glossary.md#ref-engine) suggestions for particular image names.

Having retrieved a set of reference engines (via this and other protocols), consumers can use those ref engines to recover a set of [Merkle roots](glossary.md#merkle-root) potentially associated with a given image name.
Consumers who choose not to support this specification can safely ignore the remainder of this document.
Consumers who choose to support this specification MAY attempt to discover and use ref engines via other channels, and only fall back to this protocol if those ref engines do not return a satisfactory Merkle root.

## Regexp ref-engines objects

This section defines the `application/vnd.oci.regexp-ref-engines.v1+json` [media type][media-type].
Content of this type MUST be a JSON object, as defined in [RFC 7159 section 4][rfc7159-s4].
Keys MUST be Extended Regular Expressions, as defined in [IEEE Std 1003.1-2008][ERE].
Values MUST be JSON objects that conform to the [`application/vnd.oci.ref-engines.v1+json` media type](well-known-uri-ref-engine-discovery.md#ref-engines-objects).

For a given image name, consumers SHOULD treat all keys that match the image name as valid.
When multiple keys match the image name, consumers SHOULD prefer the regexp with the longest length.
When multiple keys of the same length match the image name, consumers SHOULD prefer the regexp which sorts earlier according to `LC_COLLATE` in the POSIX locale, as defined in [IEEE Std 1003.1-2008][POSIX-LC_COLLATE].

## XDG representation

Consumers discovering ref engines for an image name SHOULD lookup the name in `$XDG_CONFIG_DIRS/oci-discovery/ref-engine-discovery.json`, as defined in the [XDG Base Directory Specification 0.8][XDG].
When `oci-discovery/ref-engine-discovery.json` is located under multiple base directories, consumers SHOULD merge the configurations.

When merging multiple [`application/vnd.oci.regexp-ref-engines.v1+json` objects](#regexp-ref-engines-objects), the result MUST be another `application/vnd.oci.regexp-ref-engines.v1+json` object.
For each root key in any source configuration, the merged configuration MUST have a root entry for that key, the value of which MUST match the value for that key from the most-preferred source configuration with an entry for that key.

### Example

```
$ cat ~/.config/oci-discovery/ref-engine-discovery.json
{
  "^[^/]*example\.com/.*$": {
    "refEngines": [
      {
        "protocol": "oci-index-template-v1",
        "uri": "https://{host}/ref/{name}"
      }
    ]
  },
  "^a\.example\.com/app#.*$": {
    "refEngines": [
      {
        "protocol": "oci-index-template-v1",
        "uri": "https://{host}/oci-ref/{name}"
      }
    ],
    "casEngines": [
      {
        "protocol": "oci-cas-template-v1",
        "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
      }
    ]
  }
}
```

The [`oci-index-template-v1` protocol](index-template.md) is [registered](ref-engine-protocols.md).
The [`oci-cas-template-v1` protocol](cas-template.md) is [registered](cas-engine-protocols.md).

With this configuration, an image named `a.example.com/app#1.0` will match both entries.
A `^a\.example\.com/app#.*$` is longer (24 characters to `^[^/]*example\.com/.*$`'s 22), so it is the preferred match.
A client would check the `oci-index-template-v1` ref engine at `https://{host}/ref/{name}` first, and then fall back to the `oci-index-template-v1` ref engine at `https://{host}/oci-ref/{name}` if further [Merkle roots](glossary.md#merkle-root) were needed.

[ERE]: http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap09.html#tag_09_04
[media-type]: https://tools.ietf.org/html/rfc6838
[POSIX-LC_COLLATE]: http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap07.html#tag_07_03_02_06
[rfc7159-s4]: https://tools.ietf.org/html/rfc7159#section-4
[rfc7159-s5]: https://tools.ietf.org/html/rfc7159#section-5
[XDG]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-0.8.html
