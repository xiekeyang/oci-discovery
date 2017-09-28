# Serving everything from one Nginx server

This provides a experiment of how to set up a discovery server by nginx. It is useful for integration test.

## Structure

Publishers who intend to serve discoverable images via the protocols in this repository, but who only want to serve static content can use [Nginx][] with a [configuration file](nginx.conf):

The Nginx server stores [ref-engines object](../../xdg-ref-engine-discovery.md#ref-engines-objects) under backend path `/srv/example.com/.well-known/oci-host-ref-engines`.

With above pattern, consumers will attempt to resolve image names matching the `{HOST}/app#…` family of [host-based image names](../../host-based-image-names.md) via an [OCI Index Template](../../index-template.md) ref engine at `https://{HOST}/oci-index/app`.
Supply that by adding `application/vnd.oci.image.index.v1+json` content to `/srv/example.com/oci-index/app`:

In which the `org.opencontainers.image.ref.name` value assumes consumers will only be attempting to match the `fragment` and not the full image name; image-spec does not currently provide guidance on this point.

Supply the blobs under `/srv/example.com/oci-cas`, which are stored under `/srv/example.com/oci-cas/{alg}/{prefix}/{encoded}`.

It would be more conformant [if that content was canonical JSON][image-spec-canonical-json], but I've added newlines and indents to make the example more readable.

To publish additional images matching the `{HOST}/app#…` family of [host-based image names](../../host-based-image-names.md), add their entries to `/srv/{HOST}/oci-index/app`'s `manifests` array.
To publish additional images matching new families (e.g. `{HOST}/other-app#…`), add their entries to new `/srv/{HOST}/oci-index/` indexes (e.g. `/srv/{HOST}/oci-index/other-app`).
All the CAS blobs can go in the same bucket under `/srv/{HOST}/oci-cas`, although if you want you can adjust the `casEngines` entries and keep CAS blobs in different buckets.

## Build

Developer can build up via Dockerfile and and then run a discovery server:

```
$ docker build -t nginx:discovery-server .
$ docker run -d --name discovery-server -p 80:80 -p 443:443 nginx:discovery-server
```

> **NOTE**: Before access discovery server, developer should add
> the `*.crt` to `/usr/local/share/ca-certificates` and update it.

[Nginx]: https://nginx.org/
[image-spec-canonical-json]: https://github.com/opencontainers/image-spec/blob/v1.0.0/considerations.md#json
