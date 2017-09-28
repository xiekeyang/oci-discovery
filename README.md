# OCI Image Discovery Specifications

This repository contains two [ref-engine discovery](glossary.md#ref-engine-discovery) specifications:

* [OCI Well Known URI Ref-Engine Discovery](well-known-uri-ref-engine-discovery.md).
    There is a [Go][] implementation in [`tools/refenginediscovery/wellknownuri`](tools/refenginediscovery/wellknownuri).
    There is a [Python 3][python3] implementation in [`oci_discovery.ref_engine_discovery`](oci_discovery/ref_engine_discovery).
* [OCI XDG Ref-Engine Discovery](xdg-ref-engine-discovery.md).
    There is a Go implementation in [`tools/refenginediscovery/xdg`](tools/refenginediscovery/xdg).

This repository also contains some related specifications:

* [Host-Based Image Names](host-based-image-names.md)
    There is a Go implementation in [`tools/hostbasedimagenames`](tools/hostbasedimagenames).
    There is a [Python 3][python3] implementation in [`oci_discovery.host_based_image_names`](oci_discovery/host_based_image_names).
* [OCI Index Template Protocol](index-template.md)
    There is a Go implementation in [`tools/refengine/indextemplate`](tools/refengine/indextemplate).
    There is a Python 3 implementation in [`oci_discovery.ref_engine.oci_index_template`](oci_discovery/ref_engine/oci_index_template).
* [OCI CAS Template Protocol](cas-template.md)

This repository also contains registries for [ref-](glossary.md#ref-engine) and [CAS-engine](glossary.md#cas-engine) protocols:

* [Ref-Engine Protocols](ref-engine-prococols.md).
    There is a Go implemention in [`tools/refengine`](tools/refengine).
    There is a Python 3 implementation in [`oci_discovery.ref_engine.CONSTRUCTORS`](oci_discovery/ref_engine/__init__.py).
* [CAS-Engine Protocols](cas-engine-protocols.md).

The strategies in these specifications are inspired by some previous implementations:

* [ABD](https://github.com/appc/abd/blob/master/abd.md)
* [App Container Image Discovery](https://github.com/appc/spec/blob/v0.8.10/spec/discovery.md)
* [parcel](https://github.com/cyphar/parcel)

Examples of using the local implementations to resolve an image name are [here](tools/README.md#example) for Go and [here](oci_discovery/README.md#using-the-python-3-ref-engine-discovery-tool) for Python 3.

## Example: Serving OCI layouts from Nginx

As an alternative to the [previous example](#example-serving-everything-from-one-nginx-server), you can bucket your CAS blobs by serving [OCI layouts][layout] directly.
If your layout `index.json` are not setting `casEngines` and you are unwilling to update them to do so, you can [set `casEngines` in you ref-engines object](xdg-ref-engines-discovery.md#ref-engines-objects) at `/srv/example.com/.well-known/oci-host-ref-engines`:

```json
{
  "refEngines": [
    {
      "protocol": "oci-index-template-v1",
      "uri": "https://{host}/oci-image/{path}/index.json"
    }
  ],
  "casEngines": [
    {
      "protocol": "oci-cas-template-v1",
      "uri": "https://example.com/oci-image/{path}/blobs/{algorithm}/{encoded}"
    }
  ]
}
```

Then copy your [layout directories][layout] under `/srv/example.com/oci-image/{path}` to deploy them.

The Nginx config from the [previous example](#example-serving-everything-from-one-nginx-server) would need an adjusted [`location`][location] for the index media type:

```
location ~ ^/oci-image/.*/index.json$ {
  types  {}
  default_type  application/vnd.oci.image.index.v1+json;
  charset  utf-8;
  charset_types  *;
}
```

[Go]: https://golang.org/
[image-spec]: https://github.com/opencontainers/image-spec
[layout]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-layout.md
[location]: http://nginx.org/en/docs/http/ngx_http_core_module.html#location
[python3]: https://docs.python.org/3/
