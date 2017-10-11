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

import io
import logging
import os
import pathlib
import unittest
import unittest.mock

from . import xdg


class TestConfigPaths(unittest.TestCase):
    def test(self):
        home = os.path.expanduser('~')
        path = os.path.join('a', 'b')
        for environ, expected in [
                    (
                        {},
                        [
                            os.path.join(home, '.config', path),
                            os.path.join(xdg.ROOT, 'etc', 'xdg', path),
                        ],
                    ),
                    (
                        {
                            'XDG_CONFIG_HOME': os.path.join(xdg.ROOT, 'c', 'd'),
                        },
                        [
                            os.path.join(xdg.ROOT, 'c', 'd', path),
                            os.path.join(xdg.ROOT, 'etc', 'xdg', path),
                        ],
                    ),
                    (
                        {
                            'XDG_CONFIG_DIRS': os.path.join(xdg.ROOT, 'c', 'd'),
                        },
                        [
                            os.path.join(home, '.config', path),
                            os.path.join(xdg.ROOT, 'c', 'd', path),
                        ],
                    ),
                    (
                        {
                            'XDG_CONFIG_DIRS': ':'.join([
                                os.path.join(xdg.ROOT, 'c', 'd'),
                                'e',
                            ]),
                        },
                        [
                            os.path.join(home, '.config', path),
                            os.path.join(xdg.ROOT, 'c', 'd', path),
                            os.path.join('e', path),
                        ],
                    ),
                    (
                        {
                            'XDG_CONFIG_HOME': os.path.join(xdg.ROOT, 'c', 'd'),
                            'XDG_CONFIG_DIRS': ':'.join([
                                'e',
                                os.path.join(xdg.ROOT, 'f'),
                            ]),
                        },
                        [
                            os.path.join(xdg.ROOT, 'c', 'd', path),
                            os.path.join('e', path),
                            os.path.join(xdg.ROOT, 'f', path),
                        ],
                    ),
                ]:
            with self.subTest(environ=environ):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery.xdg._os.environ',
                        new=environ):
                    paths = list(xdg.config_paths(path=path))
                self.assertEqual(paths, expected)


class TestEngine(unittest.TestCase):
    @staticmethod
    def _mock_open(path):
        filename = os.path.basename(path)
        if filename == 'short':
            return io.StringIO('{"ab": "short"}')
        if filename == 'long':
            return io.StringIO('{"ab": "long", "cd": "long"}')
        if filename == 'invalid-json':
            return io.StringIO('{')
        if filename == 'non-dict':
            return io.StringIO('[]')
        if filename == 'invalid-regexp':
            return io.StringIO('{"[": "invalid-regexp"}')
        if filename == 'non-dict-value':
            return io.StringIO(r'{"^example\\.com/.*$": "non-dict"}')
        if filename == 'good':
            return io.StringIO(r"""{
              "^[^/]*example\\.com/.*$": {
                "refEngines": [
                  {
                    "protocol": "oci-index-template-v1",
                    "uri": "https://{host}/ref/{name}"
                  }
                ]
              },
              "^a\\.example\\.com/app#.*$": {
                "refEngines": [
                  {
                    "protocol": "oci-index-template-v1",
                    "uri": "https://{host}/oci-ref/{name}"
                  }
                ],
                "casEngines": [
                  {
                    "protocol": "oci-cas-template-v1",
                    "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}"
                  }
                ]
              }
            }""")
        raise FileNotFoundError()

    def test_load_config_good(self):
        def path_generator(path=None):
            for filename in ['short', 'missing-file', 'long']:
                yield os.path.join(xdg.ROOT, filename)
        short, _, long = list(path_generator())
        with unittest.mock.patch(
                target='oci_discovery.ref_engine_discovery.xdg.config_paths',
                new=path_generator):
            with unittest.mock.patch(
                    target='oci_discovery.ref_engine_discovery.xdg.open',
                    new=self._mock_open,
                    create=True):  # create=True not needed for Python 3.5+
                engine = xdg.Engine()
                config = engine._config
                keys = [key for key, _ in engine._regexps]
        self.assertEqual(
            config,
            {
                'ab': {
                    'ref_engines_object': 'short',
                    'uri': pathlib.PurePath(short).as_uri(),
                },
                'cd': {
                    'ref_engines_object': 'long',
                    'uri': pathlib.PurePath(long).as_uri(),
                },
            },
        )
        self.assertEqual(keys, ['ab', 'cd'])

    def test_load_config_bad(self):
        for name, regex in [
                (
                    'invalid-json',
                    'WARNING:oci_discovery\.ref_engine_discovery\.xdg:file:///invalid-json returned invalid JSON: .*',
                ),
                (
                    'non-dict',
                    'WARNING:oci_discovery\.ref_engine_discovery\.xdg:file:///non-dict claimed to return application/vnd\.oci\.regexp-ref-engines\.v1\+json but actually returned \[]',
                ),
                (
                    'invalid-regexp',
                    "WARNING:oci_discovery\.ref_engine_discovery\.xdg:invalid regular expression '\['",
                ),
                ]:
            with self.subTest(name=name):
                def path_generator(path=None):
                    for filename in [name, 'short']:
                        yield os.path.join(xdg.ROOT, filename)
                _, short = list(path_generator())
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery.xdg.config_paths',
                        new=path_generator):
                    with unittest.mock.patch(
                            target='oci_discovery.ref_engine_discovery.xdg.open',
                            new=self._mock_open,
                            create=True):  # create=True not needed for Python 3.5+
                        with self.assertLogs(xdg._LOGGER, level=logging.WARNING) as logs:
                            engine = xdg.Engine()
                            config = engine._config
                self.assertEqual(
                    config['ab'],
                    {
                        'ref_engines_object': 'short',
                        'uri': pathlib.PurePath(short).as_uri(),
                    },
                )
                self.assertRegex(logs.output[0], regex)

    def test_ref_engines_good(self):
        def path_generator(path=None):
            yield os.path.join(xdg.ROOT, 'good')
        good = next(path_generator())
        uri = pathlib.PurePath(good).as_uri()
        with unittest.mock.patch(
                target='oci_discovery.ref_engine_discovery.xdg.config_paths',
                new=path_generator):
            with unittest.mock.patch(
                    target='oci_discovery.ref_engine_discovery.xdg.open',
                    new=self._mock_open,
                    create=True):  # create=True not needed for Python 3.5+
                engine = xdg.Engine()
        for name, expected in [
                (
                    'a.example.com/app#1.0',
                    [
                        {
                            'config': {
                                'protocol': 'oci-index-template-v1',
                                'uri': 'https://{host}/oci-ref/{name}',
                            },
                            'casEngines': [
                                {
                                    'config': {
                                        'protocol': 'oci-cas-template-v1',
                                        'uri': 'https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}',
                                    },
                                    'uri': 'file:///good',
                                },
                            ],
                            'uri': 'file:///good',
                        },
                        {
                            'config': {
                                'protocol': 'oci-index-template-v1',
                                'uri': 'https://{host}/ref/{name}',
                            },
                            'uri': 'file:///good',
                        }
                    ],
                ),
                (
                    'b.example.com/app#1.0',
                    [
                        {
                            'config': {
                                'protocol': 'oci-index-template-v1',
                                'uri': 'https://{host}/ref/{name}',
                            },
                            'uri': 'file:///good',
                        }
                    ],
                ),
                ]:
            with self.subTest(name=name):
                references = list(engine.ref_engines(name=name))
                self.assertEqual(
                    [ref.dict() for ref in references], expected)

    def test_ref_engines_bad(self):
        def path_generator(path=None):
            yield os.path.join(xdg.ROOT, 'non-dict-value')
        with unittest.mock.patch(
                target='oci_discovery.ref_engine_discovery.xdg.config_paths',
                new=path_generator):
            with unittest.mock.patch(
                    target='oci_discovery.ref_engine_discovery.xdg.open',
                    new=self._mock_open,
                    create=True):  # create=True not needed for Python 3.5+
                engine = xdg.Engine()
                with self.assertLogs(xdg._LOGGER, level=logging.WARNING) as logs:
                    references = list(engine.ref_engines(
                        name='example.com/app#1.0'))
        self.assertRegex(
            logs.output[0],
            '^WARNING:oci_discovery\.ref_engine_discovery\.xdg:file:///non-dict-value claimed to return application/vnd\.oci\.ref-engines\.v1\+json but actually returned non-dict$')
