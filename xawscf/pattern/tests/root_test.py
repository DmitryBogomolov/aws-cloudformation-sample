import unittest
from datetime import date
from .. import root
from ...utils.loader import Custom

class TestRoot(unittest.TestCase):
    Stub = type('Stub', (), {})

    def make_stub(self, name):
        stub = self.Stub()
        stub.name = name
        return stub

    def test_get_by_name(self):
        stubs = [self.make_stub('stub-{}'.format(i + 1)) for i in range(4)]
        self.assertEqual(root.find_by_name(stubs, 'stub-1'), stubs[0])
        self.assertEqual(root.find_by_name(stubs, 'stub-3'), stubs[2])

    def test_get_function(self):
        pattern = root.Root({
            'project': 'project-1',
            'resources': {
                'f1': {'type': 'function'}
            }
        })

        self.assertIsNotNone(pattern.get_function('f1'))
        self.assertIsNone(pattern.get_function('f2'))

    def test_get_statemachine(self):
        pattern = root.Root({
            'project': 'project-1',
            'resources': {
                's1': {'type': 'statemachine'}
            }
        })

        self.assertIsNotNone(pattern.get_statemachine('s1'))
        self.assertIsNone(pattern.get_statemachine('s2'))

    def test_dump(self):
        pattern = root.Root({
            'project': 'project-1'
        })

        self.assertEqual(pattern.dump(), {
            'AWSTemplateFormatVersion': date(2010, 9, 9),
            'Transform': 'AWS::Serverless-2016-10-31',
            'Resources': {
                'SourcesBucket': {
                    'Type': 'AWS::S3::Bucket'
                }
            },
            'Outputs': {
                'SourcesBucket': {'Value': Custom('!Ref', 'SourcesBucket')}
            }
        })
