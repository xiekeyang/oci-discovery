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

from . import resolve


if 'DEBUG' in os.environ:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


class TestResolve(unittest.TestCase):
    def test(self):
        for label, name, response, expected in [
                    (
                        'success',
                        'example.com/a',
                        {
                            'refEngines': [
                                {
                                    'protocol': '_dummy',
                                    'response': [
                                        {
                                            'uri': 'https://x.example.com/y',
                                            'root': {'name': 'dummy Merkle root 1'},
                                        },
                                        {
                                            'uri': 'https://x.example.com/z',
                                            'root': {'name': 'dummy Merkle root 2'},
                                        },
                                    ],
                                }
                            ]
                        },
                        {
                            'roots': [
                                {
                                    'uri': 'https://x.example.com/y',
                                    'root': {'name': 'dummy Merkle root 1'},
                                },
                                {
                                    'uri': 'https://x.example.com/z',
                                    'root': {'name': 'dummy Merkle root 2'},
                                },
                            ],
                        }
                    ),
                ]:
            responseURI = 'https://x.example.com/y'
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery._fetch_json.fetch',
                        return_value={
                            'uri': responseURI,
                            'json': response,
                        }):
                    resolved = resolve(name=name)
                self.assertEqual(
                    resolved,
                    [
                        {'uri': responseURI, 'root': root}
                        for root in expected
                    ])


    def test_bad(self):
        for label, name, response, error, regex in [
                    (
                        'ref-engine discovery not a JSON object',
                        'example.com/a',
                        [],
                        ValueError,
                        "no Merkle root found for 'example.com/a'",
                    ),
                ]:
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine_discovery._fetch_json.fetch',
                        return_value=response):
                    self.assertRaisesRegex(error, regex, resolve, name)
