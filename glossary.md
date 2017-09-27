# Glossary

## Ref-engine discovery

A service that suggests possible [ref engines](#ref-engine) for resolving a given image name.

## CAS engine

A service that provides access to [content-addressable storage][CAS].

## Merkle root

The root node in a [Merkle tree][Merkle-tree].
In the OCI ecosystem, Merkle links are made via [descriptors][descriptor].
The Merkle root may be a descriptor ([media type][media-type] [`application/vnd.oci.descriptor.v1+json`][descriptor]), or it may have a different media type.
Merkle roots may suggest [CAS engines](#cas-engine), e.g. via a `casEngines` entry in their JSON, but that is out of scope for ref-engine discovery.

## Ref engine

A service that maps an image name to a set of potential [Merkle roots](#merkle-root).

[CAS]: https://en.wikipedia.org/wiki/Content-addressable_storage
[descriptor]: https://github.com/opencontainers/image-spec/blob/v1.0.0/descriptor.md
[media-type]: https://tools.ietf.org/html/rfc6838
[Merkle-tree]: https://en.wikipedia.org/wiki/Merkle_tree
