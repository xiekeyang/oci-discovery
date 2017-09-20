# Discovery Tools

## Example:

```
$ oci-discovery --debug resolve example.com/app#1.0 2>/tmp/log
{
  "example.com/app#1.0": [
    {
      "mediaType": "application/vnd.oci.descriptor.v1+json",
      "root": {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": "sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3"
        "size": 799,
        "annotations": {
          "org.opencontainers.image.ref.name": "1.0"
        },
        "platform": {
          "architecture": "ppc64le",
          "os": "linux"
        }
      },
      "uri": "https://example.com/oci-index/app"
    }
  ]
}
$ cat /tmp/log
time="2017-09-19T12:43:41-07:00" level=debug msg="requesting application/vnd.oci.ref-engines.v1+json from https://example.com/.well-known/oci-host-ref-engines"
time="2017-09-19T12:43:41-07:00" level=debug msg="requesting application/vnd.oci.image.index.v1+json from https://example.com/oci-index/app"
```
