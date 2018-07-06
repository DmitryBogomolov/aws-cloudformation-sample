import unittest
import os
from .. import loader

FILE_NAME = 'test.yaml'

def create_file(content):
    with open(FILE_NAME, 'w') as file_object:
        file_object.write(content)

class TestYaml(unittest.TestCase):
    def tearDown(self):
        os.remove(FILE_NAME)

    def check_load(self, content, expected):
        create_file(content)
        obj = loader.load(FILE_NAME)
        self.assertEqual(obj, expected)

    def check_save(self, obj, expected):
        loader.save(FILE_NAME, obj)
        with open(FILE_NAME, 'r') as file_object:
            content = file_object.read()
        self.assertEqual(content, expected)

    def test_load(self):
        self.check_load('a: test', {'a': 'test'})

    def test_load_intrinsic_scalar(self):
        self.check_load('a: !Ref b', {'a': loader.Custom('!Ref', 'b')})

    def test_load_intrinsic_list(self):
        self.check_load('a: !Sub [1, 2]', {'a': loader.Custom('!Sub', [1, 2])})

    def test_load_intrinsic_dict(self):
        self.check_load('a: { b: !GetAtt c.d, c: 1 }',
            {'a': {'b': loader.Custom('!GetAtt', 'c.d'), 'c': 1}})

    def test_load_intrinsic_complex(self):
        self.check_load('a: !Sub [test, { b: !Ref c, d: !GetAtt e }]', {
            'a': loader.Custom('!Sub', ['test', {
                'b': loader.Custom('!Ref', 'c'),
                'd': loader.Custom('!GetAtt', 'e')
            }])
        })

    def test_save(self):
        self.check_save({'a': 'test'}, 'a: test\n')

    def test_save_intrinsic_scalar(self):
        self.check_save({'a': loader.Custom('!Ref', 'b')}, "a: !Ref 'b'\n")

    def test_save_intrinsic_list(self):
        self.check_save({'a': loader.Custom('!Sub', [1, 2])}, "a: !Sub\n- 1\n- 2\n")

    def test_save_intrinsic_dict(self):
        self.check_save({'a': {'b': loader.Custom('!GetAtt', 'c.d'), 'c': 1}},
            "a:\n  b: !GetAtt 'c.d'\n  c: 1\n")

    def test_save_intrinsic_complex(self):
        self.check_save({
            'a': loader.Custom('!Sub', ['test', {
                'b': loader.Custom('!Ref', 'c'),
                'd': loader.Custom('!GetAtt', 'e')
            }])
        }, "a: !Sub\n- test\n- b: !Ref 'c'\n  d: !GetAtt 'e'\n")

    def test_load_with_included(self):
        with open('file1.yaml', 'w') as file_object:
            file_object.write('b: test')
        try:
            self.check_load('a: !include file1.yaml', {'a': {'b': 'test'}})
        finally:
            os.remove('file1.yaml')

    def test_load_with_included_not_exist(self):
        # pylint: disable=no-member
        with self.assertRaisesRegex(Exception, 'No such file or directory'):
            self.check_load('a: !include file1.yaml', None)

    def test_load_with_included_out_of_dir(self):
        # pylint: disable=no-member,anomalous-backslash-in-string
        with self.assertRaisesRegex(Exception, 'File path \*..\/file1.yaml\* is not valid'):
            self.check_load('a: !include ../file1.yaml', None)
