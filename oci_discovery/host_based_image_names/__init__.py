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


# The normative ABNF is in host-based-image-names.md referencing rules
# from https://tools.ietf.org/html/rfc3986#appendix-A.
_UNRESERVED_NO_HYPHEN = 'a-zA-Z0-9._~'
_SUB_DELIMS = "!$&'()*+,;="
_PCHAR = _UNRESERVED_NO_HYPHEN + '%' + _SUB_DELIMS + ':@' + '-'
_DEC_OCTET = '([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[05])'
_HEXDIG = '[0-9a-fA-F]'
_H16 = _HEXDIG + '{1,4}'
_IPv4_ADDRESS = _DEC_OCTET + '(\.' + _DEC_OCTET + '){3}'
IPv4_ADDRESS = _re.compile('^' + _IPv4_ADDRESS + '$')
_LS32 = '((' + _H16 + ':' + _H16 + ')|' + _IPv4_ADDRESS + ')'
_IPv6_ADDRESS = (
    '(' +
    '((' + _H16 + ':){6}' + _LS32 + ')|'
    '(::(' + _H16 + ':){5}' + _LS32 + ')|'
    '(' + _H16 + '?::(' + _H16 + ':){4}' + _LS32 + ')|'
    '(((' + _H16 + ':){,1}' + _H16 + ')?::(' + _H16 + ':){3}' + _LS32 + ')|'
    '(((' + _H16 + ':){,2}' + _H16 + ')?::(' + _H16 + ':){2}' + _LS32 + ')|'
    '(((' + _H16 + ':){,3}' + _H16 + ')?::' + _H16 + ':' + _LS32 + ')|'
    '(((' + _H16 + ':){,4}' + _H16 + ')?::' + _LS32 + ')|'
    '(((' + _H16 + ':){,5}' + _H16 + ')?::' + _H16 + ')|'
    '(((' + _H16 + ':){,6}' + _H16 + ')?::)'
    ')')
_IPvFUTURE = (
    'v' + _HEXDIG + '+\.' +
    '([' + _UNRESERVED_NO_HYPHEN + _SUB_DELIMS + ':' + '-' + '])+')
_IP_LITERAL = r'\[(' + _IPv6_ADDRESS + '|' + _IPvFUTURE + ')]'
_REG_NAME = '[' + _UNRESERVED_NO_HYPHEN + '%' + _SUB_DELIMS + '-]*'
_HOST_BASED_IMAGE_NAME_REGEX = _re.compile(
    '^(?P<host>' + _IP_LITERAL + '|' + _IPv4_ADDRESS + '|' + _REG_NAME + ')'
    '/'
    '(?P<path>[' + _PCHAR + ']+(/[' + _PCHAR + ']*)*)'
    '(#(?P<fragment>[/?' + _PCHAR + ']*))?$')


def parse(name):
    """Parse a host-based image name.

    Following host-based-image-names.md.
    """
    match = _HOST_BASED_IMAGE_NAME_REGEX.match(name)
    if match is None:
        raise ValueError(
            '{!r} does not match the host-based-image-name pattern'
            .format(name))
    groups = match.groupdict()
    if groups['fragment'] is None:
        groups['fragment'] = ''
    return groups
