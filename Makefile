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

all: oci-discovery

.PHONY: oci-discovery
oci-discovery:
	go build -o oci-discovery ./tools/cmd

test: test-go test-python

test-debug: test-go-debug test-python-debug

test-go:
	go test ./tools/...

test-go-debug:
	go test -v ./tools/...

test-python:
	python3 -m unittest discover

test-python-debug:
	DEBUG=1 python3 -m unittest discover -v

clean:
	rm -f oci-discovery
