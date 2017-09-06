# OCI Index Template Protocol

This is version 1 of this specification.

The index-template protocol is configured via a single [URI Template][rfc6570].
When configured via a [`refEngines` entry](ref-engine-discovery.md#ref-engines-objects), the `uri` property MUST be set, and its value is the URI Template.

Consumers MUST provide at least the following variables:

* `name`, matching `host-based-image-name` in the [`host-based-image-name` rule](host-based-image-names.md).
* `host`, matching `host` in the `host-based-image-name` rule.
* `path`, matching `path-rootless` in the `host-based-image-name` rule.
* `fragment`, matching `fragment` in the `host-based-image-name` rule.
    If `fragment` was not provided in the image name, it defaults to an empty string.

and expand the URI Template as defined in [RFC 6570 section 3][rfc6570-s3].

The server providing the expanded URI MUST support requests for media type [`application/vnd.oci.image.index.v1+json`][index].
Servers MAY support other media types using HTTP content negotiation, as described in [RFC 7231 section 3.4][rfc7231-s3.4] (which is [also supported over HTTP/2][rfc7540-s8]).

Consumers retrieving `application/vnd.oci.image.index.v1+json` SHOULD process it like a [layout's `index.json`][index.json], respecting [`org.opencontainers.image.ref.name` and other annotations which are recommended for `index.json`][annotations].

## Example

An example [`refEngines` entry](ref-engine-discovery.md#ref-engines-objects) using the [registered `oci-index-template-v1` protocol identifier](ref-engine-protocols.md) is:

```json
{
  "protocol": "oci-index-template-v1",
  "uri": "https://{host}/ref/{host}/{path}"
}
```

An image name like `a.b.example.com/c/d#1.0` matches [`host-based-image-name`](host-based-image-names.md) with `a.b.example.com` as `host`, `c/d` as `path-rootless`, and `1.0` as `fragment` so the expanded URI is:

    https://a.b.example.com/ref/a.b.example.com/c/d

Retrieving that URI (with a pretend result, since [`example.com` is reserved][rfc2606-s3]):

```
$ curl -H 'Accept: application/vnd.oci.image.index.v1+json' https://a.b.example.com/ref/a.b.example.com/c/d
{
  "schemaVersion": 2,
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 799,
      "digest": "sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3",
      "platform": {
        "architecture": "ppc64le",
        "os": "linux"
      },
      "annotations": {
        "org.opencontainers.image.ref.name": "1.0"
      },
      "casEngines": [
        {
          "protocol": "oci-cas-template-v1",
          "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
        }
      ]
    },
    {
      "mediaType": "application/xml",
      "size": 7143,
      "digest": "sha256:b3d63d132d21c3ff4c35a061adf23cf43da8ae054247e32faa95494d904a007e",
      "annotations": {
        "org.freedesktop.specifications.metainfo.version": "1.0",
        "org.freedesktop.specifications.metainfo.type": "AppStream"
      },
      "casEngines": [
        {
          "protocol": "oci-cas-template-v1",
          "uri": "https://b.example.com/cas/{algorithm}/{encoded}"
        }
      ]
    }
  ]
}
```

The [`oci-cas-template-v1` protocol](cas-template.md) is [registered](cas-engine-protocols.md).

Deciding whether to look for `1.0` (the `fragment`) or the full `a.b.example.com/c/d#1.0` name is left as an exercise for the reader, as is switching based on `platform` entries or [chosing between multiple entries with the same name][duplicate-name-resolution].

[annotations]: https://github.com/opencontainers/image-spec/blob/v1.0.0/annotations.md#pre-defined-annotation-keys
[duplicate-name-resolution]: https://github.com/opencontainers/image-spec/issues/588#event-1080723646
[index]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-index.md
[index.json]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-layout.md#indexjson-file
[rfc2606-s3]: https://tools.ietf.org/html/rfc2606#section-3
[rfc6570]: https://tools.ietf.org/html/rfc6570
[rfc6570-s3]: https://tools.ietf.org/html/rfc6570#section-3
[rfc7231-s3.4]: https://tools.ietf.org/html/rfc7231#section-3.4
[rfc7540-s8]: https://tools.ietf.org/html/rfc7540#section-8
