#!/usr/bin/env python3

import unittest
import os
import helper

class TestHelper(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
