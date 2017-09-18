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
from .. import ref_engine as _ref_engine
from . import ancestor_hosts as _ancestor_hosts


_LOGGER = _logging.getLogger(__name__)


def resolve(name, protocols=('https', 'http'), port=None):
    """Resolve an image name to a Merkle root.

    Implementing ref-engine-discovery.md
    """
    name_parts = _host_based_image_names.parse(name=name)
    for protocol in protocols:
        for host in _ancestor_hosts.ancestor_hosts(host=name_parts['host']):
            if port:
                host = '{}:{}'.format(host, port)
            uri = '{}://{}/.well-known/oci-host-ref-engines'.format(
                protocol, host)
            _LOGGER.debug('discovering ref engines via {}'.format(uri))
            try:
                ref_engines_object = _fetch_json.fetch(
                    uri=uri,
                    media_type='application/vnd.oci.ref-engines.v1+json')
            except (_ssl.CertificateError,
                    _ssl.SSLError,
                    _urllib_error.URLError) as error:
                _LOGGER.warning('failed to fetch {} ({})'.format(uri, error))
                continue
            _LOGGER.debug('received ref-engine discovery object:\n{}'.format(
                _pprint.pformat(ref_engines_object)))
            if not isinstance(ref_engines_object, dict):
                _LOGGER.warning(
                    '{} claimed to return application/vnd.oci.ref-engines.v1+json but actually returned {}'
                    .format(uri, ref_engines_object),
                )
                continue
            for ref_engine_object in ref_engines_object.get('refEngines', []):
                try:
                    ref_engine = _ref_engine.new(**ref_engine_object)
                except KeyError as error:
                    _LOGGER.warning(error)
                    continue
                try:
                    roots = list(ref_engine.resolve(name=name))
                except (_ssl.CertificateError, _ssl.SSLError) as error:
                    _LOGGER.warning(
                        'failed to resolve {!r} via {} ({})'.format(
                            name, ref_engine, error))
                    continue
                except _urllib_error.HTTPError as error:
                    _LOGGER.warning('failed to fetch {} ({})'.format(
                        error.geturl(), error))
                    continue
                except Exception as error:
                    _LOGGER.warning(error)
                    continue
                if roots:
                    data = {'roots': roots}
                    if 'casEngines' in ref_engines_object:
                        data['casEngines'] = ref_engines_object['casEngines']
                    return data
                else:
                    _LOGGER.debug('{} returned no results for {}'.format(
                        ref_engine, name))
    raise ValueError('no Merkle root found for {!r}'.format(name))
