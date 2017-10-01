This package contains a [Python 3][python3] implementation of various oci-discovery specifications.

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
  "example.com/app#1.0": [
    {
      "mediaType": "application/vnd.oci.descriptor.v1+json",
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
$ cat /tmp/log
DEBUG:oci_discovery.ref_engine_discovery.well_known_uri:discovering ref engines via https://example.com/.well-known/oci-host-ref-engines
WARNING:oci_discovery.ref_engine_discovery.well_known_uri:failed to fetch https://example.com/.well-known/oci-host-ref-engines (<urlopen error [SSL: UNKNOWN_PROTOCOL] unknown protocol (_ssl.c:600)>)
DEBUG:oci_discovery.ref_engine_discovery.well_known_uri:discovering ref engines via http://example.com/.well-known/oci-host-ref-engines
DEBUG:oci_discovery.ref_engine_discovery.well_known_uri:received ref-engine discovery object:
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

[pip]: https://pip.pypa.io/en/stable/
[python3]: https://docs.python.org/3/
[uritemplate]: https://pypi.python.org/pypi/uritemplate
[rfc6570]: https://tools.ietf.org/html/rfc6570
[signed-name-assertions]: https://github.com/opencontainers/image-spec/issues/176
