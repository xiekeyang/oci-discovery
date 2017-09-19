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

import re
import unittest

from . import parse, IPv4_ADDRESS, _IP_LITERAL #v6_ADDRESS


class TestIPv4Detection(unittest.TestCase):
    def test_ipv4(self):
        for host, expected in [
                    ('0.0.0.0', True),
                    ('9.0.0.0', True),
                    ('10.0.0.0', True),
                    ('99.0.0.0', True),
                    ('100.0.0.0', True),
                    ('199.0.0.0', True),
                    ('200.0.0.0', True),
                    ('249.0.0.0', True),
                    ('250.0.0.0', True),
                    ('255.0.0.0', True),
                    ('256.0.0.0', False),
                    ('260.0.0.0', False),
                    ('300.0.0.0', False),
                    ('0.0.0', False),
                    ('0.0.0.0.0', False),
                    ('example.com', False),
                ]:
            with self.subTest(host=host):
                match = IPv4_ADDRESS.match(host)
                self.assertEqual(match is not None, expected)


class TestIPv6Detection(unittest.TestCase):
    def test_ipv6(self):
        regexp = re.compile('^' + _IP_LITERAL + '$')
        for host, expected in [
                    ('[::1]', True),
                    ('9.0.0.0', False),
                    ('10.0.0.0', False),
                    ('99.0.0.0', False),
                    ('100.0.0.0', False),
                    ('199.0.0.0', False),
                    ('200.0.0.0', False),
                    ('249.0.0.0', False),
                    ('250.0.0.0', False),
                    ('255.0.0.0', False),
                    ('256.0.0.0', False),
                    ('260.0.0.0', False),
                    ('300.0.0.0', False),
                    ('0.0.0', False),
                    ('0.0.0.0.0', False),
                    ('example.com', False),
                ]:
            with self.subTest(host=host):
                match = regexp.match(host)
                self.assertEqual(match is not None, expected)


class TestImageNameParsing(unittest.TestCase):
    def test_good(self):
        for (name, expected) in [
                    ('example.com/a', {
                        'host': 'example.com',
                        'path': 'a',
                        'fragment': '',
                    }),
                    ('example.com/a/', {
                        'host': 'example.com',
                        'path': 'a/',
                        'fragment': '',
                    }),
                    ('example.com/a/b', {
                        'host': 'example.com',
                        'path': 'a/b',
                        'fragment': '',
                    }),
                    ('example.com/a/b#c', {
                        'host': 'example.com',
                        'path': 'a/b',
                        'fragment': 'c',
                    }),
                    ('localhost/a', {
                        'host': 'localhost',
                        'path': 'a',
                        'fragment': '',
                    }),
                    ('127.0.0.1/a', {
                        'host': '127.0.0.1',
                        'path': 'a',
                        'fragment': '',
                    }),
                    ('[::1]/a', {
                        'host': '[::1]',
                        'path': 'a',
                        'fragment': '',
                    }),
                ]:
            with self.subTest(name=name):
                match = parse(name=name)
                self.assertEqual(match, expected)

    def test_bad(self):
        for name in [
                    'example.com',
                    '/',
                    'example.com/',
                    'example.com/#',
                    'example.com:80/a',
                    '[::1]:80/a',
                ]:
            with self.subTest(name=name):
                self.assertRaises(ValueError, parse, name)
