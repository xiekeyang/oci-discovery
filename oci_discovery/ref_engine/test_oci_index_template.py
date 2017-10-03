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
            responseURI = 'https://x.example.com/y'
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine.oci_index_template._fetch_json.fetch',
                        return_value={
                            'uri': responseURI,
                            'json': response,
                        }):
                    resolved = list(engine.resolve(name=name))
                self.assertEqual(
                    resolved,
                    [
                        {
                            'mediaType': 'application/vnd.oci.descriptor.v1+json',
                            'root': root,
                            'uri': responseURI,
                        }
                        for root in expected
                    ])

    def test_bad(self):
        uri = 'https://example.com/index'
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
            engine = oci_index_template.Engine(uri=uri)
            with self.subTest(label=label):
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine.oci_index_template._fetch_json.fetch',
                        return_value={
                            'uri': uri,
                            'json': response,
                        }):
                    generator = engine.resolve(name='example.com/a')
                    self.assertRaisesRegex(error, regex, list, generator)

    def test_reference_expansion(self):
        response = {
            'manifests': [
                {
                    'entry': 'a',
                    'annotations': {
                        'org.opencontainers.image.ref.name': '1.0',
                    },
                },
            ],
        }
        for uri, base, expected in [
                    (
                        'index.json',
                        'https://example.com/a',
                        'https://example.com/index.json',
                    ),
                    (
                        'index.json',
                        'https://example.com/a/',
                        'https://example.com/a/index.json',
                    ),
                    (
                        'https://{host}/{path}#{fragment}',
                        'https://a.example.com/b/',
                        'https://example.com/a#1.0'
                    ),
                    (
                        '//{host}/{path}#{fragment}',
                        'https://a.example.com/b/',
                        'https://example.com/a#1.0'
                    ),
                    (
                        '/{path}#{fragment}',
                        'https://b.example.com/c/',
                        'https://b.example.com/a#1.0',
                    ),
                    (
                        '{path}#{fragment}',
                        'https://b.example.com/c/',
                        'https://b.example.com/c/a#1.0',
                    ),
                    (
                        '#{fragment}',
                        'https://example.com/a',
                        'https://example.com/a#1.0',
                    ),
                    (
                        '#{fragment}',
                        'https://example.com/a/',
                        'https://example.com/a/#1.0',
                    ),
                ]:
            with self.subTest(label='{} from {}'.format(uri, base)):
                engine = oci_index_template.Engine(uri=uri, base=base)
                with unittest.mock.patch(
                        target='oci_discovery.ref_engine.oci_index_template._fetch_json.fetch',
                        return_value={
                            'uri': expected,
                            'json': response
                        }) as mock:
                    resolved = list(engine.resolve(name='example.com/a#1.0'))
                    mock.assert_called_with(
                        uri=expected,
                        media_type='application/vnd.oci.image.index.v1+json')
                self.assertEqual(
                    resolved,
                    [
                        {
                            'mediaType': 'application/vnd.oci.descriptor.v1+json',
                            'root': root,
                            'uri': expected,
                        }
                        for root in response['manifests']
                    ])
