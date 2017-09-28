# Discovery Tools

This is a Go interface implementation to resolve image names potential [Merkle roots](../glossary.md#merkle-root).

## Build

Build the oci-discovery executable from the project root with:
```
$ make oci-discovery
```

## Example

Execute the subcommand `resolve` in `oci-discovery` with the example [Nginx server](../contrib/nginx):

```
$ oci-discovery --debug resolve example.com/app#1.0 2>/tmp/log
{
  "example.com/app#1.0": [
    {
      "casEngines": [
        {
          "config": {
            "protocol": "oci-cas-template-v1",
            "uri": "/cas/{algorithm}/{encoded}"
          },
          "uri": "https://example.com/.well-known/oci-host-ref-engines"
        }
      ],
      "mediaType": "application/vnd.oci.descriptor.v1+json",
      "root": {
        "digest": "sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3",
        "annotations": {
          "org.opencontainers.image.ref.name": "1.0"
        },
        "casEngines": [
          {
            "protocol": "oci-cas-template-v1",
            "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
          }
        ],
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "platform": {
          "architecture": "ppc64le",
          "os": "linux"
        },
        "size": 799
      },
      "uri": "https://example.com/oci-index/app"
    }
  ]
}
$ cat /tmp/log
time="2017-09-19T12:43:41-07:00" level=debug msg="requesting application/vnd.oci.ref-engines.v1+json from https://example.com/.well-known/oci-host-ref-engines"
time="2017-09-19T12:43:41-07:00" level=debug msg="requesting application/vnd.oci.image.index.v1+json from https://example.com/oci-index/app"
```
