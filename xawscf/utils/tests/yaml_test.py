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

    def test_load(self):
        create_file('Test: a')
        self.assertEqual(yaml.load(FILE_NAME), { 'Test': 'a' })

    def test_save(self):
        yaml.save(FILE_NAME, { 'Test': 'a' })
        with open(FILE_NAME, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Test: a\n')
