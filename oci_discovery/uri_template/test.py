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

import collections
import unittest

try:
    import uritemplate
except ImportError:
    uritemplate = None


from . import URITemplate


class TestURITemplate(unittest.TestCase):
    def _run(self, cls, exceptions=(), wrong_values=()):
        """Test against examples from RFC 6570.

        https://tools.ietf.org/html/rfc6570
        """
        # Defined in https://tools.ietf.org/html/rfc6570#section-3.2
        # Other sections have their own definitions, but they're
        # subsets of this set.
        variables = {
            'count': ('one', 'two', 'three'),
            'dom': ('example', 'com'),
            'dub': 'me/too',
            'hello': 'Hello World!',
            'half': '50%',
            'var': 'value',
            'who': 'fred',
            'base': 'http://example.com/home/',
            'path': '/foo/bar',
            'list': ('red', 'green', 'blue'),
            'keys': collections.OrderedDict((
                ('semi', ';'),
                ('dot', '.'),
                ('comma', ','),
            )),
            'v': '6',
            'x': '1024',
            'y': '768',
            'empty': '',
            'empty_keys': {},
            #'undef': None.
        }
        for name, checks in (
                    (
                        'section 1.2, level 1',
                        (
                            ('{var}', 'value'),
                            ('{hello}', 'Hello%20World%21'),
                        ),
                    ),
                    (
                        'section 1.2, level 2',
                        (
                            ('{+var}', 'value'),
                            ('{+hello}', 'Hello%20World!'),
                            ('{+path}/here', '/foo/bar/here'),
                            ('here?ref={+path}', 'here?ref=/foo/bar'),
                            ('X#{var}', 'X#value'),
                            ('X#{hello}', 'X#Hello%20World!'),
                        ),
                    ),
                    (
                        'section 1.2, level 3',
                        (
                            ('map?{x,y}', 'map?1024,768'),
                            ('{x,hello,y}', '1024,Hello%20World%21,768'),
                            ('{+x,hello,y}', '1024,Hello%20World!,768'),
                            ('{+path,x}/here', '/foo/bar,1024/here'),
                            ('{#x,hello,y}', '#1024,Hello%20World!,768'),
                            ('{#path,x}/here', '#/foo/bar,1024/here'),
                            ('X{.var}', 'X.value'),
                            ('X{.x,y}', 'X.1024.768'),
                            ('{/var}', '/value'),
                            ('{/var,x}/here', '/value/1024/here'),
                            ('{;x,y}', ';x=1024;y=768'),
                            ('{;x,y,empty}', ';x=1024;y=768;empty'),
                            ('{?x,y}', '?x=1024&y=768'),
                            ('{?x,y,empty}', '?x=1024&y=768&empty='),
                            ('?fixed=yes{&x}', '?fixed=yes&x=1024'),
                            ('{&x,y,empty}', '&x=1024&y=768&empty='),
                        ),
                    ),
                    (
                        'section 1.2, level 4',
                        (
                            ('{var:3}', 'val'),
                            ('{var:30}', 'value'),
                            ('{list}', 'red,green,blue'),
                            ('{list*}', 'red,green,blue'),
                            ('{keys}', 'semi,%3B,dot,.,comma,%2C'),
                            ('{keys*}', 'semi=%3B,dot=.,comma=%2C'),
                            ('{+path:6}/here', '/foo/b/here'),
                            ('{+list}', 'red,green,blue'),
                            ('{+list*}', 'red,green,blue'),
                            ('{+keys}', 'semi,;,dot,.,comma,,'),
                            ('{+keys*}', 'semi=;,dot=.,comma=,'),
                            ('{#path:6}/here', '#/foo/b/here'),
                            ('{#list}', '#red,green,blue'),
                            ('{#list*}', '#red,green,blue'),
                            ('{#keys}', '#semi,;,dot,.,comma,,'),
                            ('{#keys*}', '#semi=;,dot=.,comma=,'),
                            ('X{.var:3}', 'X.val'),
                            ('X{.list}', 'X.red,green,blue'),
                            ('X{.list*}', 'X.red.green.blue'),
                            ('X{.keys}', 'X.semi,%3B,dot,.,comma,%2C'),
                            ('X{.keys*}', 'X.semi=%3B.dot=..comma=%2C'),
                            ('{/var:1,var}', '/v/value'),
                            ('{/list}', '/red,green,blue'),
                            ('{/list*}', '/red/green/blue'),
                            ('{/list*,path:4}', '/red/green/blue/%2Ffoo'),
                            ('{/keys}', '/semi,%3B,dot,.,comma,%2C'),
                            ('{/keys*}', '/semi=%3B/dot=./comma=%2C'),
                            ('{;hello:5}', ';hello=Hello'),
                            ('{;list}', ';list=red,green,blue'),
                            ('{;list*}', ';list=red;list=green;list=blue'),
                            ('{;keys}', ';keys=semi,%3B,dot,.,comma,%2C'),
                            ('{;keys*}', ';semi=%3B;dot=.;comma=%2C'),
                            ('{?var:3}', '?var=val'),
                            ('{?list}', '?list=red,green,blue'),
                            ('{?list*}', '?list=red&list=green&list=blue'),
                            ('{?keys}', '?keys=semi,%3B,dot,.,comma,%2C'),
                            ('{?keys*}', '?semi=%3B&dot=.&comma=%2C'),
                            ('{&var:3}', '&var=val'),
                            ('{&list}', '&list=red,green,blue'),
                            ('{&list*}', '&list=red&list=green&list=blue'),
                            ('{&keys}', '&keys=semi,%3B,dot,.,comma,%2C'),
                            ('{&keys*}', '&semi=%3B&dot=.&comma=%2C'),
                        ),
                    ),
                    (
                        'section 3.2.2',
                        (
                            ('{var}', 'value'),
                            ('{hello}', 'Hello%20World%21'),
                            ('{half}', '50%25'),
                            ('O{empty}X', 'OX'),
                            ('O{undef}X', 'OX'),
                            ('{x,y}', '1024,768'),
                            ('{x,hello,y}', '1024,Hello%20World%21,768'),
                            ('?{x,empty}', '?1024,'),
                            ('?{x,undef}', '?1024'),
                            ('?{undef,y}', '?768'),
                            ('{var:3}', 'val'),
                            ('{var:30}', 'value'),
                            ('{list}', 'red,green,blue'),
                            ('{list*}', 'red,green,blue'),
                            ('{keys}', 'semi,%3B,dot,.,comma,%2C'),
                            ('{keys*}', 'semi=%3B,dot=.,comma=%2C'),
                        ),
                    ),
                ):
            with self.subTest(name=name):
                for template, expected in checks:
                    with self.subTest(template=template):
                        if template in exceptions and template in wrong_values:
                            self.fail(
                                msg="entries in both 'exceptions' and 'wrong_values'.  Pick one.")
                        obj = cls(uri=template)
                        self.assertEqual(str(obj), template)
                        try:
                            expanded = obj.expand(**variables)
                        except Exception as error:
                            if template in exceptions:
                                self.skipTest(
                                    reason='expected failure: raised {}'
                                        .format(error))
                            raise
                        if template in exceptions:
                            self.fail(
                                msg='expected a failure, but this no longer raises an exception')
                        if template in wrong_values:
                            self.assertNotEqual(expanded, expected)
                        else:
                            self.assertEqual(expanded, expected)

    def test_stub(self):
        self._run(
            cls=URITemplate,
            exceptions={
                '?fixed=yes{&x}',
                '?{undef,y}',
                '?{x,empty}',
                '?{x,undef}',
                'O{undef}X',
                'X{.keys*}',
                'X{.keys}',
                'X{.list*}',
                'X{.list}',
                'X{.var:3}',
                'X{.var}',
                'X{.x,y}',
                'here?ref={+path}',
                'map?{x,y}',
                '{#keys*}',
                '{#keys}',
                '{#list*}',
                '{#list}',
                '{#path,x}/here',
                '{#path:6}/here',
                '{#x,hello,y}',
                '{&keys*}',
                '{&keys}',
                '{&list*}',
                '{&list}',
                '{&var:3}',
                '{&x,y,empty}',
                '{+hello}',
                '{+keys*}',
                '{+keys}',
                '{+list*}',
                '{+list}',
                '{+path,x}/here',
                '{+path:6}/here',
                '{+path}/here',
                '{+var}',
                '{+x,hello,y}',
                '{/keys*}',
                '{/keys}',
                '{/list*,path:4}',
                '{/list*}',
                '{/list}',
                '{/var,x}/here',
                '{/var:1,var}',
                '{/var}',
                '{;hello:5}',
                '{;keys*}',
                '{;keys}',
                '{;list*}',
                '{;list}',
                '{;x,y,empty}',
                '{;x,y}',
                '{?keys*}',
                '{?keys}',
                '{?list*}',
                '{?list}',
                '{?var:3}',
                '{?x,y,empty}',
                '{?x,y}',
                '{keys*}',
                '{list*}',
                '{undef,y}',
                '{x,hello,y}',
                '{x,y}',
            },
            wrong_values={
                'X#{hello}',
                '{half}',
                '{hello}',
                '{keys}',
                '{list}',
                '{var:30}',
                '{var:3}',
            },
        )

    @unittest.skipIf(uritemplate is None, 'failed to import uritemplate')
    def test_external(self):
        self._run(
            cls=uritemplate.URITemplate,
            wrong_values={
                'X#{hello}',
                'X{.keys*}',
                'X{.keys}',
                '{#keys*}',
                '{#keys}',
                '{&keys*}',
                '{&keys}',
                '{+keys*}',
                '{+keys}',
                '{/keys*}',
                '{/keys}',
                '{;keys*}',
                '{;keys}',
                '{?keys*}',
                '{?keys}',
                '{keys*}',
                '{keys}',
            },
        )
