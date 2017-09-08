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

from . import parse


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
                ]:
            with self.subTest(name=name):
                self.assertRaises(ValueError, parse, name)
