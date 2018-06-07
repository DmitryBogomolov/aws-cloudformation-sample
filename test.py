#!/usr/bin/env python3

import unittest
import os

from utils import yaml
yaml.load = lambda _: { 'project': 'test', 'bucket': 'test' }

from utils import helper
# TODO: utils.pattern.py is imported - find a way to stub it.
from commands import deploy_sources

class Tester(object):
    def __init__(self, **kwargs):
        self.data = kwargs

    def get(self, name):
        return self.data[name]

class TestHelper(unittest.TestCase):
    def test_get_pattern_path(self):
        self.assertEqual(helper.get_pattern_path(),
            os.path.realpath('pattern.yaml'))

    def test_get_processed_template_path(self):
        self.assertEqual(helper.get_processed_template_path(),
            os.path.realpath('.package/template.yaml'))

    def test_get_archive_name(self):
        cases = [
            ('test.t1', 'test_t1.zip'),
            ('src/test.t2', 'src_test_t2.zip'),
            ('./src/test.t2', 'src_test_t2.zip'),
            ('src/dir1/dir2/test.t4', 'src_dir1_dir2_test_t4.zip'),
            ('src', 'src.zip'),
            ('src/dir1/dir2', 'src_dir1_dir2.zip')
        ]

        for code_uri, expected in cases:
            self.assertEqual(helper.get_archive_name(code_uri), expected, code_uri)

        with self.assertRaises(RuntimeError):
            helper.get_archive_name('/src/test')

    def test_get_archive_path(self):
        self.assertEqual(helper.get_archive_path('test.zip'), os.path.realpath('.package/test.zip'))

    def test_get_code_uri_list(self):
        functions = [
            Tester(code_uri='uri-1'),
            Tester(code_uri='uri-2'),
            Tester(code_uri='uri-3'),
            Tester(code_uri='uri-2'),
            Tester(code_uri='uri-2'),
            Tester(code_uri='uri-3'),
            Tester(code_uri='uri-4')
        ]
        self.assertEqual(helper.get_code_uri_list(functions),
            ['uri-1', 'uri-2', 'uri-3', 'uri-4'])

    def test_select_functions(self):
        pattern = Tester()
        functions = []
        for name in ['f1', 'f2', 'f3', 'f4']:
            function = Tester()
            function.name = name
            functions.append(function)
        pattern.functions = functions
        cases = [
            (None, functions),
            ('f2,f3', [functions[1], functions[2]]),
            ('f4,f5', [functions[3]]),
            ('', functions)
        ]

        for filter_value, expected in cases:
            self.assertEqual(list(helper.select_functions(pattern, filter_value)), expected)


class TestDeploySources(unittest.TestCase):
    def test_get_s3_key(self):
        pattern = Tester(project='proj1')
        self.assertEqual(deploy_sources.get_s3_key(pattern, 'obj1'), 'proj1/obj1')

if __name__ == '__main__':
    unittest.main()
