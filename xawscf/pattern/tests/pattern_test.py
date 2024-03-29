import unittest
import os
from .. import pattern
from ...utils.helper import PATTERN_NAME

class TestPattern(unittest.TestCase):
    def test_get_pattern(self):
        with open(PATTERN_NAME, mode='w', encoding='utf-8') as file_object:
            file_object.write('Test: test')

        try:
            obj = pattern.get_pattern('')

            self.assertIsInstance(obj, pattern.Root)
        finally:
            os.remove(PATTERN_NAME)

    def test_get_pattern_named(self):
        name = PATTERN_NAME + '1'
        with open(name, mode='w', encoding='utf-8') as file_object:
            file_object.write('Test: test')

        try:
            obj = pattern.get_pattern(name)

            self.assertIsInstance(obj, pattern.Root)
        finally:
            os.remove(name)
