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

class URITemplate(object):
    """Stub implementation of uritemplate's URITemplate.

    https://pypi.python.org/pypi/uritemplate
    """
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return self.uri

    def expand(self, **kwargs):
        # Basic URI Templates match Python's str.format() syntax, just
        # try that.
        try:
            return self.uri.format(**kwargs)
        except KeyError as error:
            raise ValueError(
                'failed to format {}'.format(self.uri)
            ) from error
