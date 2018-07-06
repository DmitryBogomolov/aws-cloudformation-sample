import unittest
from .. import base

class TestBase(unittest.TestCase):
    def test_get(self):
        obj = base.Base({
            'a': 1,
            'b': 'test'
        })

        self.assertEqual(obj.get('a'), 1)
        self.assertEqual(obj.get('b', 'non'), 'test')
        self.assertEqual(obj.get('c', 2), 2)

    def test_get_default(self):
        obj = base.Base({})

        self.assertEqual(obj.get('d', ''), '')
        # pylint: disable=no-member
        with self.assertRaisesRegex(KeyError, 'Field "d" is not defined.'):
            obj.get('d')

    def test_get_path(self):
        obj = base.Base({
            'a1': 1,
            'a2': {
                'b1': 2,
                'b2': {
                    'c1': 3
                }
            }
        })

        self.assertEqual(obj.get_path('a1'), 1)
        self.assertEqual(obj.get_path('a2.b1'), 2)
        self.assertEqual(obj.get_path('a2.b2.c1'), 3)

    def test_get_path_default(self):
        obj = base.Base({
            'a2': {
                'b1': 2
            }
        })

        self.assertEqual(obj.get_path('a1', 2), 2)
        self.assertEqual(obj.get_path('a1.b1', 3), 3)
        self.assertEqual(obj.get_path('a2.b2', 4), 4)

        # pylint: disable=no-member
        with self.assertRaisesRegex(KeyError, 'Field "a1" in "a1" is not defined.'):
            obj.get_path('a1')
        # pylint: disable=no-member
        with self.assertRaisesRegex(KeyError, 'Field "a1" in "a1.b1" is not defined.'):
            obj.get_path('a1.b1')
        # pylint: disable=no-member
        with self.assertRaisesRegex(KeyError, 'Field "b2" in "a2.b2" is not defined.'):
            obj.get_path('a2.b2')
