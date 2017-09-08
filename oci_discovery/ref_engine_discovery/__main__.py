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

import argparse
import json
import logging
import sys

from . import resolve


logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

parser = argparse.ArgumentParser(
    description='Resolve image names via OCI Ref-engine Discovery.')
parser.add_argument(
    'names', metavar='NAME', type=str, nargs='+',
    help='a host-based image name')
parser.add_argument(
    '-l', '--log-level',
    choices=['critical', 'error', 'warning', 'info', 'debug'],
    help='Log verbosity.  Defaults to {!r}.'.format(
        logging.getLevelName(log.level).lower()))
parser.add_argument(
    '--https-only',
    action='store_const',
    const=True,
    help='Log verbosity.  Defaults to {!r}.'.format(
        logging.getLevelName(log.level).lower()))

args = parser.parse_args()

if args.log_level:
    level = getattr(logging, args.log_level.upper())
    log.setLevel(level)

protocols = ['https']
if not args.https_only:
    protocols.append('http')

resolved = {}
for name in args.names:
    try:
        resolved[name] = resolve(name=name, protocols=protocols)
    except ValueError as error:
        log.error(error)
json.dump(
    resolved,
    sys.stdout,
    indent=2,
    sort_keys=True)
sys.stdout.write('\n')
