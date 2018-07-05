import unittest
from .. import cloudformation

StubCloudFormation = type('StubCloudFormation', (), {})

class TestCloudFormation(unittest.TestCase):
    def test_get_stack_info(self):
        data = {
            'stack-1': {'Stacks': [{'tag': 'test-stack-1'}]}
        }
        # pylint: disable=invalid-name
        def describe_stacks(StackName):
            return data[StackName]
        stub = StubCloudFormation()
        stub.describe_stacks = describe_stacks

        self.assertEqual(cloudformation.get_stack_info(stub, 'stack-1'), {'tag': 'test-stack-1'})

    def test_get_sources_bucket(self):
        outputs = [
            {'OutputKey': 'key-1'},
            {'OutputKey': 'SourcesBucket', 'OutputValue': 'test-bucket-1'},
            {'OutputKey': 'key-2'}
        ]
        data = {
            'stack-1': {'Stacks': [{'Outputs': outputs}]}
        }
        # pylint: disable=invalid-name
        def describe_stacks(StackName):
            return data[StackName]
        stub = StubCloudFormation()
        stub.describe_stacks = describe_stacks

        self.assertEqual(cloudformation.get_sources_bucket(stub, 'stack-1'), 'test-bucket-1')
