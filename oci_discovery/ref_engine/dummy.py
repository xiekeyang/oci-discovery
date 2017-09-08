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

import copy as _copy


class Engine(object):
    """Dummy ref engine for testing.

    So we don't have to hit the network to test resolution.
    """
    def __str__(self):
        return '<{}.{} response={}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self._response)

    def __init__(self, response):
        self._response = response

    def resolve(self, name):
        return _copy.deepcopy(self._response)