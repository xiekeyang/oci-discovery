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

import email.message
import unittest
import unittest.mock

from . import fetch


class HTTPResponse(object):
    def __init__(self, code=200, body=None, headers=None):
        self.code = code
        self._body = body
        self.headers = email.message.Message()
        for key, value in headers.items():
            self.headers[key] = value

    def read(self):
        return self._body or ''


class TestFetchJSON(unittest.TestCase):
    def test_good(self):
        for name, response, expected in [
                    (
                        'empty object',
                        HTTPResponse(
                            body=b'{}',
                            headers={
                                'Content-Type': 'application/json; charset=UTF-8',
                            },
                        ),
                        {},
                    ),
                    (
                        'basic object',
                        HTTPResponse(
                            body=b'{"a": "b", "c": 1}',
                            headers={
                                'Content-Type': 'application/json; charset=UTF-8',
                            },
                        ),
                        {'a': 'b', 'c': 1},
                    ),
                ]:
            with self.subTest(name=name):
                with unittest.mock.patch(
                            target='oci_discovery.fetch_json._urllib_request.urlopen',
                            return_value=response
                        ) as patch_context:
                    json = fetch(uri='https://example.com')
                self.assertEqual(json, expected)

    def test_bad(self):
        for name, response, error, regex in [
                    (
                        'no charset',
                        HTTPResponse(
                            body=b'{}',
                            headers={
                                'Content-Type': 'application/json',
                            },
                        ),
                        ValueError,
                        'https://example.com does not declare a charset'
                    ),
                    (
                        'declared charset does not match body',
                        HTTPResponse(
                            body=b'\xff',
                            headers={
                                'Content-Type': 'application/json; charset=UTF-8',
                            },
                        ),
                        ValueError,
                        'https://example.com returned content which did not match the declared utf-8 charset'
                    ),
                    (
                        'invalid JSON',
                        HTTPResponse(
                            body=b'{',
                            headers={
                                'Content-Type': 'application/json; charset=UTF-8',
                            },
                        ),
                        ValueError,
                        'https://example.com returned invalid JSON'
                    ),
                    (
                        'unexpected media type',
                        HTTPResponse(
                            body=b'{}',
                            headers={
                                'Content-Type': 'text/plain; charset=UTF-8',
                            },
                        ),
                        ValueError,
                        'https://example.com returned text/plain, not application/json'
                    ),
                ]:
            with self.subTest(name=name):
                with unittest.mock.patch(
                        target='oci_discovery.fetch_json._urllib_request.urlopen',
                        return_value=response):
                    self.assertRaisesRegex(
                        error, regex, fetch, 'https://example.com')
