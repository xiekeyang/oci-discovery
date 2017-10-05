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
import os as _os
import pathlib as _pathlib
import pprint as _pprint
import re as _re

from . import yield_from_ref_engines_object as _yield_from_ref_engines_object


_LOGGER = _logging.getLogger(__name__)

ROOT = _os.path.splitdrive(_os.path.expanduser('~'))[0]
if not ROOT:
    ROOT = _os.sep


def config_paths(path):
    """Yield $XDG_CONFIG_DIRS/path in order of decreasing preference.

    Paths will be yielded regardless of whether they exist on the
    filesystem.
    """
    default_home = _os.path.join(_os.path.expanduser('~'), '.config')
    home = _os.environ.get('XDG_CONFIG_HOME', default_home)
    yield _os.path.join(home, path)
    default_dirs = _os.path.join(ROOT, 'etc', 'xdg')
    dirs = _os.environ.get('XDG_CONFIG_DIRS', default_dirs)
    for dirname in dirs.split(':'):
        yield _os.path.join(dirname, path)


class Engine(object):
    def __init__(self, subdir='oci-discovery'):
        self.subdir = subdir
        self.load_config()

    def merged_config(self):
        config = {}
        tail = _os.path.join(self.subdir, 'ref-engine-discovery.json')
        for path in config_paths(path=tail):
            uri = _pathlib.PurePath(path).as_uri()
            path = _os.path.abspath(path)
            try:
                with open(path) as f:
                    this_config = _json.load(f)
            except FileNotFoundError:
                continue
            except ValueError as error:
                _LOGGER.warning('{} returned invalid JSON: {}'.format(uri, error))
                continue
            if not isinstance(this_config, dict):
                media_type = 'application/vnd.oci.regexp-ref-engines.v1+json'
                _LOGGER.warning(
                    '{} claimed to return {} but actually returned {}'
                    .format(uri, media_type, this_config),
                )
                continue
            for key, value in sorted(this_config.items()):
                if key in config:
                    continue
                _LOGGER.debug('load {!r} from {}'.format(key, uri))
                config[key] = {
                    'uri': uri,
                    'ref_engines_object': value,
                }
        return config

    def load_config(self):
        self._config = self.merged_config()
        keys = sorted(
            self._config.keys(),
            key=lambda key: (-len(key), key),
        )
        self._regexps = []
        for key in keys:
            try:
                regexp = _re.compile(key)
            except Exception as error:
                _LOGGER.warning('invalid regular expression {!r}'.format(key))
                continue
            self._regexps.append((key, regexp))

    def ref_engines(self, name):
        """Resolve an image name to a Merkle root.

        Implementing xdg-ref-engine-discovery.md
        """
        for key, regexp in self._regexps:
            if regexp.search(name):
                config = self._config[key]
                _LOGGER.debug('{!r} matched {!r} from {}'.format(
                    name, key, config['uri']))
                _LOGGER.debug(
                    'matched ref-engine discovery object:\n{}'.format(
                        _pprint.pformat(config['ref_engines_object'])))
                try:
                    yield from _yield_from_ref_engines_object(**config)
                except ValueError as error:
                    _LOGGER.warning(error)
                    continue
