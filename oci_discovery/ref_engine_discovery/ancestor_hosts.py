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

import re as _re


# Based on rules from https://tools.ietf.org/html/rfc3986#appendix-A.
_DEC_OCTET = '([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[05])'
_IP_V4_REGEXP = _re.compile(
    '^' + _DEC_OCTET + '(\.' + _DEC_OCTET + '){3}$')


def ancestor_hosts(host):
    """Iterate through a host and its DNS ancestors.

    Following ref-engine-discovery.md#images-associated-with-a-hosts-oci-host-ref-engines
    """
    if host[0] == '[':
        yield host
        return  # no ancestor domains for IP-literals
    match = _IP_V4_REGEXP.match(host)
    if match is not None:
        yield host
        return  # no ancestor domains for IPv4 addresses
    segments = host.split('.')
    for i in range(len(segments) - 1):
        yield '.'.join(segments[i:])
