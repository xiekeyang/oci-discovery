# OCI Image Discovery Specifications

This repository contains the [OCI Ref-Engine Discovery specification](ref-engine-discovery.md) and related specifications as an extention to the [image specification][image-spec]:

* [Host-Based Image Names](host-based-image-names.md)
    There is a [Python 3][python3] implementation in [`oci_discovery.host_based_image_names`](oci_discovery/host_based_image_names).
* [OCI Ref-Engine Discovery](ref-engine-discovery.md).
    There is a Python 3 implementation in [`oci_discovery.ref_engine_discovery`](oci_discovery/ref_engine_discovery).
* [OCI Index Template Protocol](index-template.md)
    There is a Python 3 implementation in [`oci_discovery.ref_engine.oci_index_template`](oci_discovery/ref_engine/oci_index_template).
* [OCI CAS Template Protocol](cas-template.md)

This repository also contains registries for ref- and CAS-engine protocols:

* [Ref-Engine Protocols](ref-engine-prococols.md).
    There is a Python 3 implementation in [`oci_discovery.ref_engine.CONSTRUCTORS`](oci_discovery/ref_engine/__init__.py).
* [CAS-Engine Protocols](cas-engine-protocols.md).

The strategies in these specifications are inspired by some previous implementations:

* [ABD](https://github.com/appc/abd/blob/master/abd.md)
* [App Container Image Discovery](https://github.com/appc/spec/blob/v0.8.10/spec/discovery.md)
* [parcel](https://github.com/cyphar/parcel)

## Python dependencies

The [OCI Index Template Protocol](index-template.md) [implementation](oci_discovery/ref_engine/oci_index_template) depends on the [uritemplate][] package.
You can install the dependencies with [pip][]:

```
$ pip install -r requirements.txt
```

When uritemplate is not installed, a local implementation is used instead.
But the local stub supports only the most basic [URI Templates][rfc6570].

## Using the Python 3 ref-engine discovery tool

The individual components are usable as libraries, but the ref-engine discovery implementation can also be used from the command line:

```
$ python3 -m oci_discovery.ref_engine_discovery -l debug example.com/app#1.0 2>/tmp/log
{
  "example.com/app#1.0": {
    "roots": [
      {
        "root": {
          "annotations": {
            "org.opencontainers.image.ref.name": "1.0"
          },
          "casEngines": [
            {
              "protocol": "oci-cas-template-v1",
              "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
            }
          ],
          "digest": "sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3",
          "mediaType": "application/vnd.oci.image.manifest.v1+json",
          "platform": {
            "architecture": "ppc64le",
            "os": "linux"
          },
          "size": 799
        },
        "uri": "http://example.com/oci-index/app"
      }
    ]
  }
}
$ cat /tmp/log
DEBUG:oci_discovery.ref_engine_discovery:discovering ref engines via https://example.com/.well-known/oci-host-ref-engines
WARNING:oci_discovery.ref_engine_discovery:failed to fetch https://example.com/.well-known/oci-host-ref-engines (<urlopen error [SSL: UNKNOWN_PROTOCOL] unknown protocol (_ssl.c:600)>)
DEBUG:oci_discovery.ref_engine_discovery:discovering ref engines via http://example.com/.well-known/oci-host-ref-engines
DEBUG:oci_discovery.ref_engine_discovery:received ref-engine discovery object:
{'refEngines': [{'protocol': 'oci-index-template-v1',
                 'uri': 'http://{host}/oci-index/{path}'}]}
DEBUG:oci_discovery.ref_engine.oci_index_template:fetching an OCI index for example.com/app#1.0 from http://example.com/oci-index/app
DEBUG:oci_discovery.ref_engine.oci_index_template:received OCI index object:
{'manifests': [{'annotations': {'org.opencontainers.image.ref.name': '1.0'},
                'casEngines': [{'protocol': 'oci-cas-template-v1',
                                'uri': 'https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}'}],
                'digest': 'sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3',
                'mediaType': 'application/vnd.oci.image.manifest.v1+json',
                'platform': {'architecture': 'ppc64le', 'os': 'linux'},
                'size': 799},
               {'annotations': {'org.freedesktop.specifications.metainfo.type': 'AppStream',
                                'org.freedesktop.specifications.metainfo.version': '1.0'},
                'casEngines': [{'protocol': 'oci-cas-template-v1',
                                'uri': 'https://b.example.com/cas/{algorithm}/{encoded}'}],
                'digest': 'sha256:b3d63d132d21c3ff4c35a061adf23cf43da8ae054247e32faa95494d904a007e',
                'mediaType': 'application/xml',
                'size': 7143}],
 'schemaVersion': 2}
```

Consumers who are trusting images based on the ref-engine discovery and ref-engine servers are encouraged to use `--protocol=https`.

Consumers who are trusting images based on a property of the Merkle tree (e.g. [like this][signed-name-assertions]) can safely perform ref-engine discovery and ref-resolution over HTTP, although they may still want to use `--protocol=https` to protect from sniffers.

## Example: Serving everything from one Nginx server

Publishers who intend to serve discoverable images via the protocols in this repository, but who only want to serve static content can use [Nginx][] with a configuration like:

```
events {
  worker_connections 1024;
}

http {
  # you may need to configure these if you lack write access to the
  # default locations, depending on which features are compiled into
  # your Nginx.
  client_body_temp_path /some/where/client_temp;
  proxy_temp_path /some/where/proxy_temp;
  fastcgi_temp_path /some/where/fastcgi_temp;
  scgi_temp_path /some/where/scgi_temp;
  uwsgi_temp_path /some/where/uwsgi_temp;

  server {
    listen  80;
    listen  [::]:80;
    server_name  example.com;

    location / {
      return  301 https://$host$request_uri;
    }
  }

  server {
    listen  443 ssl;
    listen  [::]:443 ssl;
    server_name  example.com;

    ssl_certificate  /etc/ssl/example.com/fullchain.pem;
    ssl_certificate_key  /etc/ssl/example.com/privkey.pem;

    root /srv/example.com;

    location /.well-known/oci-host-ref-engines {
      types  {}
      default_type  application/vnd.oci.ref-engines.v1+json;
      charset  utf-8;
      charset_types  *;
    }

    location /oci-index {
      types  {}
      default_type  application/vnd.oci.image.index.v1+json;
      charset  utf-8;
      charset_types  *;
    }
  }
}
```

Then in `/srv/example.com/.well-known/oci-host-ref-engines`, the following [ref-engines object](ref-engine-discovery.md#ref-engines-objects):

```json
{
  "refEngines": [
    {
      "protocol": "oci-index-template-v1",
      "uri": "https://{host}/oci-index/{path}"
    }
  ]
}
```

With that pattern, consumers will attempt to resolve image names matching the `example.com/app#…` family of [host-based image names](host-based-image-names.md) via an [OCI Index Template](index-template.md) ref engine at `https://example.com/oci-index/app`.
Supply that by adding `application/vnd.oci.image.index.v1+json` content to `/srv/example.com/oci-index/app`:

```json
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
          "uri": "https://example.com/oci-cas/{algorithm}/{encoded:2}/{encoded}"
        }
      ]
    }
  ]
}
```

The `org.opencontainers.image.ref.name` value assumes consumers will only be attempting to match the `fragment` and not the full image name; image-spec does not currently provide guidance on this point.

Supply the blobs under `/srv/example.com/oci-cas`.  For example, `/srv/example.com/oci-cas/sha256/e9/e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3` would contain:

```json
{
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": 7023,
    "digest": "sha256:b5b2b2c507a0944348e0303114d8d93aaaa081732b86451d9bce1f432a537bc7"
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 32654,
      "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f"
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 16724,
      "digest": "sha256:3c3a4604a545cdc127456d94e421cd355bca5b528f4a9c1905b15da2eb4a4c6b"
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 73109,
      "digest": "sha256:ec4b8955958665577945c89419d1af06b5f7636b4ac3da7f12184802ad867736"
    }
  ]
}
```

It would be more conformant [if that content was canonical JSON][image-spec-canonical-json], but I've added newlines and indents to make the example more readable.

To publish additional images matching the `example.com/app#…` family of [host-based image names](host-based-image-names.md), add their entries to `/srv/example.com/oci-index/app`'s `manifests` array.
To publish additional images matching new families (e.g. `example.com/other-app#…`), add their entries to new `/srv/example.com/oci-index/` indexes (e.g. `/srv/example.com/oci-index/other-app`).
All the CAS blobs can go in the same bucket under `/srv/example.com/oci-cas`, although if you want you can adjust the `casEngines` entries and keep CAS blobs in different buckets.

## Example: Serving OCI layouts from Nginx

As an alternative to the [previous example](#example-serving-everything-from-one-nginx-server), you can bucket your CAS blobs by serving [OCI layouts][layout] directly.
If your layout `index.json` are not setting `casEngines` and you are unwilling to update them to do so, you can [set `casEngines` in you ref-engines object](ref-engine-discovery.md#ref-engines-objects) at `/srv/example.com/.well-known/oci-host-ref-engines`:

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

[image-spec]: https://github.com/opencontainers/image-spec
[image-spec-canonical-json]: https://github.com/opencontainers/image-spec/blob/v1.0.0/considerations.md#json
[layout]: https://github.com/opencontainers/image-spec/blob/v1.0.0/image-layout.md
[location]: http://nginx.org/en/docs/http/ngx_http_core_module.html#location
[Nginx]: https://nginx.org/
[pip]: https://pip.pypa.io/en/stable/
[python3]: https://docs.python.org/3/
[rfc6570]: https://tools.ietf.org/html/rfc6570
[signed-name-assertions]: https://github.com/opencontainers/image-spec/issues/176
[uritemplate]: https://pypi.python.org/pypi/uritemplate
