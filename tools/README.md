# Discovery Tools

## Eaxmple:

```
$ go run tools/cmd/main.go --debug discovery example.com/app#1.0
[
	{
		"mediaType": "application/vnd.oci.image.manifest.v1+json",
		"digest": "sha256:e9770a03fbdccdd4632895151a93f9af58bbe2c91fdfaaf73160648d250e6ec3",
		"size": 799,
		"annotations": {
			"org.opencontainers.image.ref.name": "1.0"
		},
		"platform": {
			"architecture": "ppc64le",
			"os": "linux"
		}
	}
]
```
