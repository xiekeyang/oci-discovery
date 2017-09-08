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

import unittest
import unittest.mock

from . import oci_index_template


class TestEngine(unittest.TestCase):
    def test_good(self):
        for label, name, response, expected in [
                    (
                        'empty fragment returns all entries',
                        'example.com/a',
                        {
                            'manifests': [
                                {
                                    'entry': 'a',
                                },
                                {
                                    'entry': 'b',
                                    'annotations': {
                                        'org.opencontainers.image.ref.name': '1.0',
                                    },
                                },
                            ],
                        },
                        [
                            {
                                'entry': 'a',
                            },
                            {
                                'entry': 'b',
                                'annotations': {
                                    'org.opencontainers.image.ref.name': '1.0',
                                },
                            },
                        ],
                    ),
                    (
                        'nonempty fragment returns only matching entries',
                        'example.com/a#1.0',
                        {
                            'manifests': [
                                {
                                    'entry': 'a',
                                },
                                {
                                    'entry': 'b',
                                    'annotations': {
                                        'org.opencontainers.image.ref.name': '1.0',
                                    },
                                },
                            ],
                        },
                        [
                            {
                                'entry': 'b',
                                'annotations': {
                                    'org.opencontainers.image.ref.name': '1.0',
                                },
                            },
                        ],
                    ),
                    (
                        'unmatched nonempty fragment returns no entries',
                        'example.com/a#2.0',
                        {
                            'manifests': [
                                {
                                    'entry': 'a',
                                },
                                {
                                    'entry': 'b',
                                    'annotations': {
                                        'org.opencontainers.image.ref.name': '1.0',
                                    },
                                },
                            ],
                        },
                        [],
                    ),
                ]:
            engine = oci_index_template.Engine(uri='https://example.com/index')
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine.oci_index_template._fetch_json.fetch',
                        return_value=response):
                    resolved = list(engine.resolve(name=name))
                self.assertEqual(resolved, expected)

    def test_bad(self):
        for label, response, error, regex in [
                    (
                        'index is not a JSON object',
                        [],
                        ValueError,
                        'https://example.com/index claimed to return application/vnd.oci.image.index.v1\+json, but actually returned \[]',
                    ),
                    (
                        'manifests is not a JSON array',
                        {'manifests': {}},
                        ValueError,
                        "https://example.com/index claimed to return application/vnd.oci.image.index.v1\+json, but actually returned \{'manifests': \{}}",
                    ),
                    (
                        'manifests contains a non-object',
                        {'manifests': [None]},
                        ValueError,
                        "https://example.com/index claimed to return application/vnd.oci.image.index.v1\+json, but actually returned \{'manifests': \[None]}",
                    ),
                    (
                        'at least one manifests[].annotations is not a JSON object',
                        {'manifests': [{'annotations': None}]},
                        ValueError,
                        "https://example.com/index claimed to return application/vnd.oci.image.index.v1\+json, but actually returned \{'manifests': \[\{'annotations': None}]}",
                    ),
                ]:
            engine = oci_index_template.Engine(uri='https://example.com/index')
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine.oci_index_template._fetch_json.fetch',
                        return_value=response):
                    generator = engine.resolve(name='example.com/a')
                    self.assertRaisesRegex(error, regex, list, generator)