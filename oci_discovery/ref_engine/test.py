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

from . import new


class TestNew(unittest.TestCase):
    def test_good(self):
        uri = 'https://{host}/ref/{name}'
        engine = new(
            protocol='oci-index-template-v1',
            uri=uri)
        self.assertEqual(
            str(engine),
            '<oci_discovery.ref_engine.oci_index_template.Engine uri={}>'
                .format(uri))

    def test_bad(self):
        self.assertRaisesRegex(
            ValueError,
            "unsupported ref-engine protocol 'unregistered'",
            new,
            protocol='unregistered')
