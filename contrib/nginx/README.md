# Serving everything from one Nginx server

Publishers who intend to serve discoverable images via the protocols in this repository, but who only want to serve static content can use [Nginx][].
This example walks you through one possible approach.

The [Nginx configuration file](nginx.conf) is fairly straightforward, redirecting HTTP requests to HTTPS, and serving HTTPS out of `/srv/example.com` with some media type overrides to get proper typing for [ref-engines objects](../../xdg-ref-engine-discovery.md#ref-engines-objects) and [OCI indexes][index].

The [ref-engines object](../../xdg-ref-engine-discovery.md#ref-engines-objects) for the [OCI Well-Known URI Ref-Engine Discovery specification](../../well-known-uri-ref-engine-discovery.md) is served from `/srv/example.com/.well-known/oci-host-ref-engines` with example content like [this](example.com/.well-known/oci-host-ref-engines).

With the [example ref-engines object](example.com/.well-known/oci-host-ref-engines), consumers will attempt to resolve image names matching the `example.com/app#…` family of [host-based image names](../../host-based-image-names.md) via an [OCI Index Template](../../index-template.md) ref engine at `https://example.com/oci-index/app`.
That [index][] is served from `/srv/example.com/oci-index/app` with example content like [this](example.com/oci-index/app).

The `org.opencontainers.image.ref.name` value in [the example index](example.com/oci-index/app) assumes consumers will only be attempting to match the `fragment` and not the full image name; image-spec does not currently provide guidance on this point.

The `casEngines` entry in [the example index](example.com/oci-index/app) suggests consumers retrieve CAS blobs from `https://example.com/oci-cas/{algorithm}/{encoded:2}/{encoded}`.
Supply those blobs at `/srv/example.com/oci-cas/{algorithm}/{encoded:2}/{encoded}`.
For example `sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3` is at [`/srv/example.com/oci-cas/sha256/e9/e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3`](example.com/oci-cas/sha256/e9/e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3).
It would be more conformant [if that content was canonical JSON][image-spec-canonical-json], but I've added newlines and indents to make the example more readable.

To publish additional images matching the `example.com/app#…` family of [host-based image names](../../host-based-image-names.md), add their entries to [`/srv/example.com/oci-index/app`](example.com/oci-index/app)'s `manifests` array.
To publish additional images matching new families (e.g. `example.com/other-app#…`), add their entries to new `/srv/example.com/oci-index/` indexes (e.g. `/srv/example.com/oci-index/other-app`).
All the CAS blobs can go in the same bucket under `/srv/example.com/oci-cas`, although if you want you can adjust the `casEngines` entries and keep CAS blobs in different buckets.

## Example: Serving OCI layouts from Nginx

As an alternative to the [previous example](#serving-everything-from-one-nginx-server), you can bucket your CAS blobs by serving [OCI layouts][layout] directly.
If your layout `index.json` are not setting `casEngines` and you are unwilling to update them to do so, you can [set `casEngines` in you ref-engines object](../../xdg-ref-engine-discovery.md#ref-engines-objects) at `/srv/example.com/.well-known/oci-host-ref-engines` with example content like [this](layouts/example.com/.well-known/oci-host-ref-engines).

Then copy your [layout directories][layout] under `/srv/example.com/oci-image/{path}` to deploy them (like [this](layouts/example.com/oci-image)).

The [Nginx config](nginx.conf) from the [previous example](#serving-everything-from-one-nginx-server) would need an adjusted [`location`][location] for the index media type, resulting in [this](layouts/nginx.conf).

## Build

You can build a Docker image using the provided [`Dockerfile`](Dockerfile):

```
$ docker build -t nginx:discovery-server .
```

Then run a discovery server:

```
$ docker run -d --name discovery-server -p 80:80 -p 443:443 nginx:discovery-server
```

> **NOTE**: Before accessing the discovery server, you should add [`example.crt`](ssl/example.com/example.crt) to `/usr/local/share/ca-certificates` and run [`update-ca-certificates`][update-ca-certificates.8] or similar.
>
> Alternatively, adjust the [Nginx config](nginx.conf) to serve `/srv/example.com` directly (instead of redirecting to HTTPS) and use the HTTP protocol for testing, resulting in [this](nginx-http.conf).

[image-spec-canonical-json]: https://github.com/opencontainers/image-spec/blob/v1.0.0/considerations.md#json
[index]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-index.md
[layout]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-layout.md
[location]: http://nginx.org/en/docs/http/ngx_http_core_module.html#location
[Nginx]: https://nginx.org/
[update-ca-certificates.8]: https://manpages.debian.org/stretch/ca-certificates/update-ca-certificates.8.en.html
