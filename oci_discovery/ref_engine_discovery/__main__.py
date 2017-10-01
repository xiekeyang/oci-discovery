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
from . import well_known_uri


logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

parser = argparse.ArgumentParser(
    description='Resolve image names via OCI Ref-Engine Discovery.')
parser.add_argument(
    'names', metavar='NAME', type=str, nargs='+',
    help='a host-based image name')
parser.add_argument(
    '-l', '--log-level',
    choices=['critical', 'error', 'warning', 'info', 'debug'],
    help='Log verbosity.  Defaults to {!r}.'.format(
        logging.getLevelName(log.level).lower()))
parser.add_argument(
    '--protocol',
    action='append',
    choices=['http', 'https'],
    help=(
        'Protocol to use for ref-engine discovery.  May be specified multiple '
        'times, in which case the protocols will be attempted in the order '
        'specified (looping through all possible hosts for the first '
        'protocol, and then through all possible hosts for the second '
        'protocol, etc.).  Defaults to https,http.'))
parser.add_argument(
    '--port',
    type=int,
    help=(
        'Port to use for ref-engine discovery.  For example, this supports '
        'connecting to test ref-engine discovery services which are not '
        "running on their protocol's usual port.  This option should be "
        'combined with a single --protocol option to avoid trying multiple '
        'protocols against the same port.'))

args = parser.parse_args()

if args.log_level:
    level = getattr(logging, args.log_level.upper())
    log.setLevel(level)

if args.protocol is None:
    args.protocol = ('https', 'http')

engines = [
    well_known_uri.Engine(protocols=args.protocol, port=args.port),
]

resolved = {}
for name in args.names:
    resolved[name] = list(resolve(engines=engines, name=name))
json.dump(
    resolved,
    sys.stdout,
    indent=2,
    sort_keys=True)
sys.stdout.write('\n')
