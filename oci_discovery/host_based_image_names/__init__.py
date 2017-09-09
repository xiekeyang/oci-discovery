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
# from https://tools.ietf.org/html/rfc3986#appendix-A.  This
# regular expression is too liberal, but will successfully match all
# valid host-based image names.
_UNRESERVED_NO_HYPHEN = 'a-zA-Z0-9._~'
_SUB_DELIMS = "!$&'()*+,;="
_PCHAR = _UNRESERVED_NO_HYPHEN + '%' + _SUB_DELIMS + ':@' + '-'
_HOST_BASED_IMAGE_NAME_REGEX = _re.compile(
    '^(?P<host>[^/]+)'
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
