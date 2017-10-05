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

import logging
import os
import unittest
import unittest.mock

from . import well_known_uri


if 'DEBUG' in os.environ:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


class TestResolve(unittest.TestCase):
    def test_good(self):
        responseURI = 'https://x.example.com/y'
        engine = well_known_uri.Engine()
        for label, name, response, expected in [
                    (
                        'only refEngines',
                        'example.com/a',
                        {
                            'refEngines': [
                                {
                                    'protocol': 'dummy ref engine 1',
                                },
                                {
                                    'protocol': 'dummy ref engine 2',
                                },
                            ]
                        },
                        [
                            {
                                'config': {
                                    'protocol': 'dummy ref engine 1',
                                },
                                'uri': responseURI,
                            },
                            {
                                'config': {
                                    'protocol': 'dummy ref engine 2',
                                },
                                'uri': responseURI,
                            },
                        ],
                    ),
                    (
                        'refEngines and casEngines',
                        'example.com/a',
                        {
                            'refEngines': [
                                {
                                    'protocol': 'dummy ref engine 1',
                                },
                                {
                                    'protocol': 'dummy ref engine 2',
                                },
                            ],
                            'casEngines': [
                                {
                                    'protocol': 'dummy CAS engine 1',
                                },
                                {
                                    'protocol': 'dummy CAS engine 2',
                                },
                            ],
                        },
                        [
                            {
                                'config': {
                                    'protocol': 'dummy ref engine 1',
                                },
                                'casEngines': [
                                    {
                                        'config': {
                                            'protocol': 'dummy CAS engine 1',
                                        },
                                        'uri': 'https://x.example.com/y',
                                    },
                                    {
                                        'config': {
                                            'protocol': 'dummy CAS engine 2',
                                        },
                                        'uri': 'https://x.example.com/y',
                                    },
                                ],
                                'uri': responseURI,
                            },
                            {
                                'config': {
                                    'protocol': 'dummy ref engine 2',
                                },
                                'casEngines': [
                                    {
                                        'config': {
                                            'protocol': 'dummy CAS engine 1',
                                        },
                                        'uri': 'https://x.example.com/y',
                                    },
                                    {
                                        'config': {
                                            'protocol': 'dummy CAS engine 2',
                                        },
                                        'uri': 'https://x.example.com/y',
                                    },
                                ],
                                'uri': responseURI,
                            },
                        ],
                    ),
                ]:
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery.well_known_uri._fetch_json.fetch',
                        return_value={
                            'uri': responseURI,
                            'json': response,
                        }):
                    resolved = [ref.dict() for ref in engine.ref_engines(name=name)]
                self.assertEqual(resolved, expected)


    def test_bad(self):
        responseURI = 'https://x.example.com/y'
        engine = well_known_uri.Engine()
        for label, name, response, regex in [
                    (
                        'ref-engine discovery not a JSON object',
                        'example.com/a',
                        [],
                        r'WARNING:oci_discovery\.ref_engine_discovery\.well_known_uri:https://x.example.com/y claimed to return application/vnd\.oci\.ref-engines\.v1\+json but actually returned \[]',
                    ),
                ]:
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery.well_known_uri._fetch_json.fetch',
                        return_value={
                            'uri': responseURI,
                            'json': response,
                        }):
                    with self.assertLogs(well_known_uri._LOGGER, level=logging.WARNING) as logs:
                        resolved = list(engine.ref_engines(name=name))
                    self.assertEqual(resolved, [])
                    self.assertRegex(logs.output[0], regex)
