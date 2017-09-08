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

from . import ancestor_hosts


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
                match = ancestor_hosts._IP_V4_REGEXP.match(host)
                self.assertEqual(match is not None, expected)


class TestAncestorHosts(unittest.TestCase):
    def test_good(self):
        for host, expected in [
                    ('example.com', ['example.com']),
                    ('a.example.com', ['a.example.com', 'example.com']),
                    ('a.b.example.com', [
                        'a.b.example.com', 'b.example.com', 'example.com']),
                    ('0.0.0.0', ['0.0.0.0']),
                    ('[::1]', ['[::1]']),
                ]:
            with self.subTest(host=host):
                uris = list(
                    ancestor_hosts.ancestor_hosts(host=host))
                self.assertEqual(uris, expected)
