# Ref-Engine Protocols

There are many possible [ref-engine](glossary.md#ref-engine) protocols.
Having identifiers for the protocols facilitates [ref-engine discovery](glossary.md#ref-engine-discovery) by allowing discovery services to [describe the protocol for suggested ref engines](well-known-uri-ref-engine-discovery.md#ref-engines-objects).
Consumers can then prefer ref engines which implement their favorite protocol and use the appropriate API to connect to them.

This section registers known protocol identifiers and maps them to their specification.
Anyone may submit new ref-engine protocol identifiers for registration.

| Protocol identifier     | Specification                                               |
|-------------------------|-------------------------------------------------------------|
| `oci-index-template-v1` | [OCI index template protocol, version 1](index-template.md) |
