# CAS-Engine Protocols

There are many possible [CAS][] engine protocols.
Having identifiers for the protocols provides a standardized way to share structured connection information.
Consumers can then prefer CAS engines which implement their favorite protocol and use the appropriate API to connect to them.

This section registers known protocol identifiers and maps them to their specification.
Anyone may submit new CAS-engine protocol identifiers for registration.

| Protocol identifier     | Specification                                           |
|-------------------------|---------------------------------------------------------|
| `oci-cas-template-v1`   | [OCI CAS template protocol, version 1](cas-template.md) |

[CAS]: https://en.wikipedia.org/wiki/Content-addressable_storage
