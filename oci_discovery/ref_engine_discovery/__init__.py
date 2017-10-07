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

from .. import ref_engine as _ref_engine


_LOGGER = _logging.getLogger(__name__)


class RefEngineReference(object):
    """Ref-engine reference yielded by Engine.ref_engines(name)."""
    def __init__(self, config, cas_engines=None, uri=None):
        self.config = config
        if cas_engines is None:
            cas_engines = []
        self.cas_engines = cas_engines
        self.uri = uri

    def dict(self):
        data = {'config': self.config}
        if self.cas_engines:
            data['casEngines'] = self.cas_engines
        if self.uri:
            data['uri'] = self.uri
        return data


def yield_from_ref_engines_object(ref_engines_object, uri):
    """Helper for application/vnd.oci.ref-engines.v1+json processing."""
    if not isinstance(ref_engines_object, dict):
        media_type = 'application/vnd.oci.ref-engines.v1+json'
        raise ValueError(
            '{} claimed to return {} but actually returned {}'
            .format(uri, media_type, ref_engines_object),
        )
    cas_engines = [
        {
            'config': cas_engine,
            'uri': uri,
        }
        for cas_engine in ref_engines_object.get('casEngines', [])
    ]
    for ref_engine_config in ref_engines_object.get('refEngines', []):
        yield RefEngineReference(
            config=ref_engine_config,
            cas_engines=cas_engines,
            uri=uri,
        )


def resolve(engines, name):
    roots = set()
    for engine in engines:
        for engine_reference in engine.ref_engines(name=name):
            # deduping here might be useful, but similar ref-engine
            # configs retrieved from different URIs might be
            # equivalent or not depending on whether (template) URIs
            # in the config are absolute or relative.
            try:
                ref_engine = _ref_engine.new(
                    base=engine_reference.uri, **engine_reference.config)
            except KeyError as error:
                _LOGGER.warning(error)
                continue
            try:
                for root in ref_engine.resolve(name=name):
                    if engine_reference.cas_engines:
                        if 'casEngines' in root:
                            root['casEngines'] = list(root['casEngines'])
                        else:
                            root['casEngines'] = []
                        root['casEngines'].extend(engine_reference.cas_engines)
                    root_hash = hash(_json.dumps(root, sort_keys=True))
                    if root_hash in roots:
                        continue
                    roots.add(root_hash)
                    yield root
            except Exception as error:
                _LOGGER.warning(error)
                continue
