# OCI CAS Template Protocol

This is version 1 of this specification.

The CAS-template protocol is configured via a single [URI Template][rfc6570].
When configured via a [`casEngines` entry](ref-engine-discovery.md#ref-engines-objects), the `uri` property MUST be set, and its value is the URI Template.

For a given blob digest, consumers MUST provide at least the following variables:

* `digest`, matching `digest` in the [`digest` rule][digest].
* `algorithm`, matching `algorithm` in the `digest` rule.
* `encoded`, matching `encoded` in the `digest` rule.

and expand the URI Template as defined in [RFC 6570 section 3][rfc6570-s3].
If the expanded URI reference is a relative reference, it MUST be resolved following [RFC 3986 section 5][rfc3986-s5].

## Example

An example [`casEngines` entry](ref-engine-discovery.md#ref-engines-objects) using the [registered `oci-cas-template-v1` protocol identifier](cas-engine-protocols.md) is:

```json
{
  "protocol": "oci-cas-template-v1",
  "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
}
```

A digest like `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` matches [`digest`][digest] with:

* `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` as `digest`,
* `sha256` as `algorithm`, and
* `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` as `encoded`

so the expanded URI is:

    https://a.example.com/cas/sha256/e3/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

[digest]: https://github.com/opencontainers/image-spec/blob/v1.0.0/descriptor.md#digests
[rfc3986-s5]: https://tools.ietf.org/html/rfc3986#section-5
[rfc6570]: https://tools.ietf.org/html/rfc6570
[rfc6570-s3]: https://tools.ietf.org/html/rfc6570#section-3
