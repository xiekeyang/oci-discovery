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

import json as _json
import logging as _logging
import urllib.request as _urllib_request


_LOGGER = _logging.getLogger(__name__)


def fetch(uri, media_type='application/json'):
    """Fetch a JSON resource."""
    with _urllib_request.urlopen(uri) as response:
        content_type = response.headers.get_content_type()
        if content_type != media_type:
            raise ValueError(
                '{} returned {}, not {}'.format(uri, content_type, media_type))
        body_bytes = response.read()
        charset = response.headers.get_content_charset()
        finalURI = response.geturl()
    if finalURI != uri:
        _LOGGER.debug('redirects lead from {} to {}'.format(uri, finalURI))
        uri = finalURI
    if charset is None:
        raise ValueError('{} does not declare a charset'.format(uri))
    try:
        body = body_bytes.decode(charset)
    except ValueError as error:
        raise ValueError(
            '{} returned content which did not match the declared {} charset'
            .format(uri, charset)) from error
    try:
        return {
            'uri': uri,
            'json': _json.loads(body),
        }
    except ValueError as error:
        raise ValueError('{} returned invalid JSON'.format(uri)) from error
