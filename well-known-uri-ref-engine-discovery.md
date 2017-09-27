# OCI Well-Known URI Ref-Engine Discovery

This is version 0.1 of this specification.

To faciliate communication between image publishers and consumers, this specification defines a [ref-engine discovery](glossary.md#ref-engine-discovery) protocol which publishers MAY use to direct consumers towards [reference engines](glossary.md#ref-engine).
Publishers who choose not to support this specification can safely ignore the remainder of this document.

Having retrieved a set of reference engines (via this and other protocols), consumers can use those ref engines to recover a set of [Merkle roots](glossary.md#merkle-root) potentially associated with a given image name.
Consumers who choose not to support this specification can safely ignore the remainder of this document.
Consumers who choose to support this specification MAY attempt to discover and use ref engines via other channels, and only fall back to this protocol if those ref engines do not return a satisfactory Merkle root.

## `oci-host-ref-engines` well-known URI registration

This specification registers the `oci-host-ref-engines` well-known URI in the Well-Known URI Registery as defined by [RFC 5785][rfc5785].

URI suffix: `oci-host-ref-engines`

Change controller: The [Open Container Initiative][OCI]

Specification document(s): This specification

Related information: None

## Images associated with a host's `oci-host-ref-engines`

Publishers SHOULD populate the `oci-host-ref-engines` resource with ref engines which are capable of resolving image names that match the [`host-based-image-name` rule](host-based-image-names.md) with a `host` part that matching their [fully qualified domain name][rfc1594-s5.2] and its subdomains or deeper descendants.
For example, `https://b.example.com/.well-known/oci-host-ref-engines` SHOULD prefer ref engines capable of resolving image names with `host` parts matching `b.example.com`, `a.b.example.com`, etc.
Some publishers MAY provide discovery services for generic image names (for example, to provide a company policy for ref-engine suggestions).
Those publishers MAY provide those recommendations via a [ref-engines resource](#ref-engines-media-types) at a URI of their choosing, but they SHOULD NOT serve the generic resource from `oci-host-ref-engines` to avoid distracting consumers following the protocol discussed in the following paragraph.

Consumers discovering ref engines for an image name that matches the [`host-based-image-name` rule](host-based-image-names.md) SHOULD request the `oci-host-ref-engines` resource from the host matching the `host` part.
If retrieving that resource fails for any reason, consumers SHOULD walk the DNS ancestors of `host`.
For example, if the `host` extracted from the image name is `a.b.example.com` and the well-known URI failed for `a.b.example.com`, the client would fall back to `b.example.com` and, if that too failed, to `example.com`.

## Ref-engines media types

Servers supporting the [`oci-host-ref-engines` URI](#oci-host-ref-engines-well-known-uri-registration) MUST support requests for media type [`application/vnd.oci.ref-engines.v1+json`](xdg-ref-engines-discovery.md#ref-engines-objects).
Servers MAY support other media types using HTTP content negotiation, as described in [RFC 7231 section 3.4][rfc7231-s3.4] (which is [also supported over HTTP/2][rfc7540-s8]).
For example, servers MAY support [`application/vnd.oci.regexp-ref-engines.v1+json`](xdg-ref-engines-discovery.md#regexp-ref-engines-objects) to provide more targetted suggestions about specific subsets of image names.

### Example 1

```
$ curl -H 'Accept: application/vnd.oci.ref-engines.v1+json' https://a.b.example.com/.well-known/oci-host-ref-engines
{
  "refEngines": [
    {
      "protocol": "oci-index-template-v1",
      "uri": "https://{host}/ref/{name}"
    },
    {
      "protocol": "docker",
      "uri": "https://index.docker.io/v2",
      "authUri": "https://auth.docker.io/token",
      "authService": "registry.docker.io",
    }
  ]
}
```

The [`oci-index-template-v1` protocol](index-template.md) is [registered](ref-engine-protocols.md).
The `docker` protocol is currently [unregistered](ref-engine-protocols.md), and is given as sketch of a possible extention protocol.

### Example 2

```
$ curl -H 'Accept: application/vnd.oci.ref-engines.v1+json' https://example.com/.well-known/oci-host-ref-engines
{
  "refEngines": [
    {
      "protocol": "oci-index-template-v1",
      "uri": "https://{host}/ref/{name}"
    }
  ],
  "casEngines": [
    {
      "protocol": "oci-cas-template-v1",
      "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
    }
  ]
}
```

The [`oci-index-template-v1` protocol](index-template.md) is [registered](ref-engine-protocols.md).
The [`oci-cas-template-v1` protocol](cas-template.md) is [registered](cas-engine-protocols.md).

[media-type]: https://tools.ietf.org/html/rfc6838
[OCI]: https://www.opencontainers.org/
[rfc1594-s5.2]: https://tools.ietf.org/html/rfc1594#section-5
[rfc5785]: https://tools.ietf.org/html/rfc5785
[rfc7159-s4]: https://tools.ietf.org/html/rfc7159#section-4
[rfc7159-s5]: https://tools.ietf.org/html/rfc7159#section-5
[rfc7231-s3.4]: https://tools.ietf.org/html/rfc7231#section-3.4
[rfc7540-s8]: https://tools.ietf.org/html/rfc7540#section-8
