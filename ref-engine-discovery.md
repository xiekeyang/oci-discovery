# OCI Ref-engine Discovery

This is version 0.1 of this specification.

To faciliate communication between image publishers and consumers, this specification defines a [ref-engine discovery](#ref-engine-discovery) protocol which publishers MAY use to direct consumers towards [reference engines](#ref-engine).
Publishers who choose not to support this specification can safely ignore the remainder of this document.

Having retrieved a set of reference engines (via this and other protocols), consumers can use those ref engines to recover a set of [Merkle roots](#merkle-root) potentially associated with a given image name.
Consumers who choose not to support this specification can safely ignore the remainder of this document.
Consumers who choose to support this specification MAY attempt to discover and use ref engines via other channels, and only fall back to this protocol if those ref engines do not return a satisfactory Merkle root.

## Glossary

### Ref-engine discovery

A service that suggests possible [ref engines](#ref-engine).
This specification defines a ref-engine discovery protocol.

### CAS engine

A service that provides access to [content-addressable storage][cas].

### Merkle root

The root node in a [Merkle tree][Merkle-tree].
In the OCI ecosystem, Merkle links are made via [descriptors][descriptor].
The Merkle root may be a descriptor ([media type][media-type] [`application/vnd.oci.descriptor.v1+json`][descriptor]), or it may have a different media type.
Merkle roots may suggest [CAS engines](#cas-engine), e.g. via a `casEngines` entry in their JSON, but that is out of scope for ref-engine discovery.

### Ref engine

A service that maps an image name to a set of potential [Merkle roots](#merkle-root).

## `oci-host-ref-engines` well-known URI registration

This specification registers the `oci-host-ref-engines` well-known URI in the Well-Known URI Registery as defined by [RFC 5785][rfc5785].

URI suffix: `oci-host-ref-engines`

Change controller: The [Open Container Initiative][OCI]

Specification document(s): This specification

Related information: None

## Images associated with a host's `oci-host-ref-engines`

Publishers SHOULD populate the `oci-host-ref-engines` resource with ref engines which are capable of resolving image names that match the [`host-based-image-name` rule](host-based-image-names.md) with a `host` part that matching their [fully qualified domain name][rfc1594-s5.2] and its subdomains or deeper descendants.
For example, https://b.example.com/.well-known/oci-host-ref-engines SHOULD prefer ref engines capable of resolving image names with `host` parts matching `b.example.com`, `a.b.example.com`, etc.
Some publishers MAY provide discovery services for generic image names (for example, to provide a company policy for ref-engine suggestions).
Those publishers MAY provide those recommendations via a [ref-engines resource](#ref-engines-media-types) at a URI of their choosing, but they SHOULD NOT serve the generic resource from `oci-host-ref-engines` to avoid distracting consumers following the protocol discussed in the following paragraph.

Consumers discovering ref-engine for an image name that matches the [`host-based-image-name` rule](host-based-image-names.md) SHOULD request the `oci-host-ref-engines` resource from the host matching the `host` part.
If retrieving that resource fails for any reason, consumers SHOULD walk the DNS ancestors of `host`.
For example, if the `host` extracted from the image name is `a.b.example.com` and the well-known URI failed for `a.b.example.com`, the client would fall back to `b.example.com` and, if that too failed, to `example.com`.

## Ref-engines media types

Servers supporting the [`oci-host-ref-engines` URI](#oci-host-ref-engines-well-known-uri-registration) MUST support requests for media type [`application/vnd.oci.ref-engines.v1+json`](#ref-engines-objects).
Servers MAY support other media types using HTTP content negotiation, as described in [RFC 7231 section 3.4][rfc7231-s3.4] (which is [also supported over HTTP/2][rfc7540-s8]).

## Ref-engines objects

This section defines the `application/vnd.oci.ref-engines.v1+json` [media type][media-type].
Content of this type MUST be a JSON object, as defined in [RFC 7159 section 4][rfc7159-s4].
The object MAY include a `refEngines` entry.
If set, the `refEngines` entry MUST be an [array][rfc7159-s5].
Each entry in the `refEngines` array MUST be an [objects][rfc7159-s4] with at least a `protocol` entry specifying the [ref-engine protocol](ref-engine-protocols.md).
Consumers SHOULD ignore entries which declare unsupported `protocol` values.
The order of entries in the array is not significant.

### Example

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

[CAS]: https://en.wikipedia.org/wiki/Content-addressable_storage
[descriptor]: https://github.com/opencontainers/image-spec/blob/v1.0.0/descriptor.md
[media-type]: https://tools.ietf.org/html/rfc6838
[Merkle-tree]: https://en.wikipedia.org/wiki/Merkle_tree
[OCI]: https://www.opencontainers.org/
[rfc1594-s5.2]: https://tools.ietf.org/html/rfc1594#section-5
[rfc5785]: https://tools.ietf.org/html/rfc5785
[rfc7159-s4]: https://tools.ietf.org/html/rfc7159#section-4
[rfc7159-s5]: https://tools.ietf.org/html/rfc7159#section-5
[rfc7231-s3.4]: https://tools.ietf.org/html/rfc7231#section-3.4
[rfc7540-s8]: https://tools.ietf.org/html/rfc7540#section-8
