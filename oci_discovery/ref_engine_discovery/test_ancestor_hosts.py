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


class TestAncestorHosts(unittest.TestCase):
    def test_good(self):
        for host, expected in [
                    ('localhost', ['localhost']),
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
