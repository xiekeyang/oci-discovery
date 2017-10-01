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

import json as __json
import logging as _logging

from .. import ref_engine as _ref_engine


_LOGGER = _logging.getLogger(__name__)


class RefEngineReference(object):
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


def resolve(engines, name):
    for engine in engines:
        for engine_reference in engine.ref_engines(name=name):
            try:
                ref_engine = _ref_engine.new(
                    base=engine_reference.uri, **engine_reference.config)
            except KeyError as error:
                _LOGGER.warning(error)
                continue
            try:
                found_root = False
                for root in ref_engine.resolve(name=name):
                    found_root = True
                    if engine_reference.cas_engines:
                        if 'casEngines' in root:
                            root['casEngines'] = list(root['casEngines'])
                        else:
                            root['casEngines'] = []
                        root['casEngines'].extend(engine_reference.cas_engines)
                    yield root
            except Exception as error:
                _LOGGER.warning(error)
                raise
                #continue
            if not found_root:
                _LOGGER.debug('{} returned no results for {}'.format(
                    ref_engine, name))
