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

import os
import unittest

from . import yield_from_ref_engines_object


class TestYieldFromRefEnginesObject(unittest.TestCase):
    def test_good(self):
        for name, ref_engines_object, expected in [
                    (
                        'one refEngines entry',
                        {
                            "refEngines": [
                                {
                                    "protocol": "oci-index-template-v1",
                                    "uri": "https://{host}/ref/{name}",
                                },
                            ],
                        },
                        [
                            {
                                'config': {
                                    'protocol': 'oci-index-template-v1',
                                    'uri': 'https://{host}/ref/{name}',
                                },
                                'uri': 'https://example.com',
                            },
                        ],
                    ),
                    (
                        'one refEngines entry and one casEngines entry',
                        {
                            "refEngines": [
                                {
                                    "protocol": "oci-index-template-v1",
                                    "uri": "https://{host}/oci-ref/{name}",
                                }
                            ],
                            "casEngines": [
                                {
                                    "protocol": "oci-cas-template-v1",
                                    "uri": "https://a.example.com/cas/{algorithm}/{encoded:2}/{encoded}",
                                },
                            ],
                        },
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
                                        'uri': 'https://example.com',
                                    },
                                ],
                                'uri': 'https://example.com',
                            },
                        ],
                    ),
                ]:
            with self.subTest(name=name):
                references = list(yield_from_ref_engines_object(
                    ref_engines_object=ref_engines_object,
                    uri='https://example.com'))
                self.assertEqual(
                    [ref.dict() for ref in references], expected)

    def test_bad(self):
        for name, ref_engines_object, regex in [
                    (
                        'ref-engine discovery not a JSON object',
                        [],
                        r'https://example.com claimed to return application/vnd\.oci\.ref-engines\.v1\+json but actually returned \[]',
                    ),
                ]:
            with self.subTest(name=name):
                generator = yield_from_ref_engines_object(
                    ref_engines_object=ref_engines_object,
                    uri='https://example.com')
                self.assertRaisesRegex(ValueError, regex, list, generator)
