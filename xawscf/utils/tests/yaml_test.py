import unittest
import os
from .. import yaml

FILE_NAME = 'test.yaml'

def create_file(content):
    with open(FILE_NAME, 'w') as f:
        f.write(content)

class TestYaml(unittest.TestCase):
    def tearDown(self):
        os.remove(FILE_NAME)

    def check_load(self, content, expected):
        create_file(content)
        obj = yaml.load(FILE_NAME)
        self.assertEqual(obj, expected)

    def check_save(self, obj, expected):
        yaml.save(FILE_NAME, obj)
        with open(FILE_NAME, 'r') as f:
            content = f.read()
        self.assertEqual(content, expected)

    def test_load(self):
        self.check_load('a: test', { 'a': 'test' })

    def test_load_intrinsic_scalar(self):
        self.check_load('a: !Ref b', { 'a': yaml.Custom('!Ref', 'b') })

    def test_load_intrinsic_list(self):
        self.check_load('a: !Sub [1, 2]', { 'a': yaml.Custom('!Sub', [1, 2]) })

    def test_load_intrinsic_dict(self):
        self.check_load('a: { b: !GetAtt c.d, c: 1 }',
            { 'a': { 'b': yaml.Custom('!GetAtt', 'c.d'), 'c': 1 } })

    def test_load_intrinsic_complex(self):
        self.check_load('a: !Sub [test, { b: !Ref c, d: !GetAtt e }]', {
            'a': yaml.Custom('!Sub', ['test', {
                'b': yaml.Custom('!Ref', 'c'),
                'd': yaml.Custom('!GetAtt', 'e')
            }])
        })

    def test_save(self):
        self.check_save({ 'a': 'test' }, 'a: test\n')

    def test_save_intrinsic_scalar(self):
        self.check_save({ 'a': yaml.Custom('!Ref', 'b') }, "a: !Ref 'b'\n")

    def test_save_intrinsic_list(self):
        self.check_save({ 'a': yaml.Custom('!Sub', [1, 2]) }, "a: !Sub\n- 1\n- 2\n")

    def test_save_intrinsic_dict(self):
        self.check_save({ 'a': { 'b': yaml.Custom('!GetAtt', 'c.d'), 'c': 1 } },
            "a:\n  b: !GetAtt 'c.d'\n  c: 1\n")

    def test_save_intrinsic_complex(self):
        self.check_save({
            'a': yaml.Custom('!Sub', ['test', {
                'b': yaml.Custom('!Ref', 'c'),
                'd': yaml.Custom('!GetAtt', 'e')
            }])
        }, "a: !Sub\n- test\n- b: !Ref 'c'\n  d: !GetAtt 'e'\n")
