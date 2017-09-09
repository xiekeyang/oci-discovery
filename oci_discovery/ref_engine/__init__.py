# Copyright 2017 oci-discovery contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import dummy as _dummy
from . import oci_index_template as _oci_index_template

# Registry for ref engines, based on ref-engine-protocols.md.
CONSTRUCTORS = {
    '_dummy': _dummy.Engine,
    'oci-index-template-v1': _oci_index_template.Engine,
}


def new(protocol, **kwargs):
    """Construct a new ref engine from a refEngines entry.

    The returned ref engine MUST provide a 'resolve' method, which
    takes an image name as a 'name' argument and returns an iterable
    of Merkle root objects.  Merkle root objects may be of any type,
    but JSON root objects SHOULD be represented as Python dicts.
    """
    try:
        constructor = CONSTRUCTORS[protocol]
    except KeyError:
        raise ValueError(
            'unsupported ref-engine protocol {!r}'.format(protocol))
    return constructor(**kwargs)
