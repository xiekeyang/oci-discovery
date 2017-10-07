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
import ssl as _ssl
import urllib.error as _urllib_error

from .. import fetch_json as _fetch_json
from .. import host_based_image_names as _host_based_image_names
from . import ancestor_hosts as _ancestor_hosts
from . import yield_from_ref_engines_object as _yield_from_ref_engines_object


_LOGGER = _logging.getLogger(__name__)


class Engine(object):
    def __init__(self, protocols=('https', 'http'), port=None):
        self.protocols = protocols
        self.port = port

    def ref_engines(self, name):
        """Resolve an image name to a Merkle root.

        Implementing well-known-uri-ref-engine-discovery.md
        """
        name_parts = _host_based_image_names.parse(name=name)
        hosts = set()
        for protocol in self.protocols:
            for host in _ancestor_hosts.ancestor_hosts(
                    host=name_parts['host']):
                if self.port:
                    host = '{}:{}'.format(host, self.port)
                if host in hosts:
                    continue  # already resolved via another protocol
                uri = '{}://{}/.well-known/oci-host-ref-engines'.format(
                    protocol, host)
                media_type = 'application/vnd.oci.ref-engines.v1+json'
                _LOGGER.debug('discovering ref engines via {}'.format(uri))
                try:
                    fetched = _fetch_json.fetch(uri=uri, media_type=media_type)
                except (_ssl.CertificateError,
                        _ssl.SSLError,
                        _urllib_error.URLError,
                        _urllib_error.HTTPError) as error:
                    _LOGGER.warning(
                        'failed to fetch {} ({})'.format(uri, error))
                    continue
                except ValueError as error:
                    _LOGGER.warning(
                        'invalid response from {} ({})'.format(uri, error))
                    continue
                ref_engines_object = fetched['json']
                _LOGGER.debug(
                    'received ref-engine discovery object:\n{}'.format(
                        _pprint.pformat(ref_engines_object)))
                hosts.add(host)
                try:
                    yield from _yield_from_ref_engines_object(
                        ref_engines_object=ref_engines_object,
                        uri=fetched['uri'],
                    )
                except ValueError as error:
                    _LOGGER.warning(error)
                    continue
