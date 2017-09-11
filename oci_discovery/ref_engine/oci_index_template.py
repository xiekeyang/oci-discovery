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

import logging as _logging
import pprint as _pprint

try:
    import uritemplate as _uritemplate
except ImportError as error:
    from .. import uri_template as _uritemplate

from .. import fetch_json as _fetch_json
from .. import host_based_image_names as _host_based_image_names


_LOGGER = _logging.getLogger(__name__)


class Engine(object):
    def __str__(self):
        return '<{}.{} uri={}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.uri_template)

    def __init__(self, uri):
        self.uri_template = _uritemplate.URITemplate(uri=uri)

    def resolve(self, name):
        name_parts = _host_based_image_names.parse(name=name)
        uri = self.uri_template.expand(**name_parts)
        _LOGGER.debug('fetching an OCI index for {} from {}'.format(name, uri))
        index = _fetch_json.fetch(
            uri=uri,
            media_type='application/vnd.oci.image.index.v1+json')
        _LOGGER.debug('received OCI index object:\n{}'.format(
            _pprint.pformat(index)))
        if not isinstance(index, dict):
            raise ValueError(
                '{} claimed to return application/vnd.oci.image.index.v1+json, but actually returned {}'
                .format(uri, index))
        if not isinstance(index.get('manifests', []), list):
            raise ValueError(
                '{} claimed to return application/vnd.oci.image.index.v1+json, but actually returned {}'
                .format(uri, index))
        for entry in index.get('manifests', []):
            if not isinstance(entry, dict):
                raise ValueError(
                    '{} claimed to return application/vnd.oci.image.index.v1+json, but actually returned {}'
                    .format(uri, index))
            annotations = entry.get('annotations', {})
            if not isinstance(annotations, dict):
                raise ValueError(
                    '{} claimed to return application/vnd.oci.image.index.v1+json, but actually returned {}'
                    .format(uri, index))
            entry_name = annotations.get(
                'org.opencontainers.image.ref.name', None)
            if (name_parts['fragment'] == '' or
                    name_parts['fragment'] == entry_name):
                yield entry
