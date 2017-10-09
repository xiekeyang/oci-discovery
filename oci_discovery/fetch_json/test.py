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


class ContextManager(object):
    def __init__(self, target, return_value):
        self._target = target
        self._return_value = return_value

    def __enter__(self):
        context = unittest.mock.MagicMock()
        context.__enter__ = lambda a: self._return_value
        context.__exit__ = lambda a, b, c, d: None
        self._patch = unittest.mock.patch(
            target=self._target, return_value=context)
        return self._patch.__enter__()

    def __exit__(self, *args, **kwargs):
        self._patch.__exit__(*args, **kwargs)


class HTTPResponse(object):
    def __init__(self, url, redirect=None, code=200, body=None, headers=None):
        self._url = url
        self._redirect = redirect
        self.code = code
        self._body = body
        self.headers = email.message.Message()
        for key, value in headers.items():
            self.headers[key] = value

    def geturl(self):
        if self._redirect:
            return self._redirect
        return self._url

    def read(self):
        return self._body or ''


class TestFetchJSON(unittest.TestCase):
    def test_good(self):
        uri = 'https://example.com'
        for name, response, expected in [
                    (
                        'empty object',
                        HTTPResponse(
                            url=uri,
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
                            url=uri,
                            body=b'{"a": "b", "c": 1}',
                            headers={
                                'Content-Type': 'application/json; charset=UTF-8',
                            },
                        ),
                        {'a': 'b', 'c': 1},
                    ),
                ]:
            with self.subTest(name=name):
                with ContextManager(
                        target='oci_discovery.fetch_json._urllib_request.urlopen',
                        return_value=response):
                    fetched = fetch(uri=uri)
                self.assertEqual(fetched, {'uri': uri, 'json': expected})

    def test_bad(self):
        uri = 'https://example.com'
        for name, response, error, regex in [
                    (
                        'no charset',
                        HTTPResponse(
                            url=uri,
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
                            url=uri,
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
                            url=uri,
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
                            url=uri,
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
                with ContextManager(
                        target='oci_discovery.fetch_json._urllib_request.urlopen',
                        return_value=response):
                    self.assertRaisesRegex(
                        error, regex, fetch, 'https://example.com')

    def test_redirect(self):
        initial_uri = 'https://example.com'
        final_uri = 'https://example.com/redirect'
        response = HTTPResponse(
            url=initial_uri,
            redirect=final_uri,
            body=b'{}',
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
            },
        )
        with ContextManager(
                target='oci_discovery.fetch_json._urllib_request.urlopen',
                return_value=response):
            fetched = fetch(uri=initial_uri)
        self.assertEqual(fetched, {'uri': final_uri, 'json': {}})
