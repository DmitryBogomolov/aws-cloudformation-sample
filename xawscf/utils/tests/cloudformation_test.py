import unittest
import os
import boto3
from ..const import SOURCES_BUCKET
from ..helper import PATTERN_NAME
from .. import cloudformation
from .. import client

class TestCloudFormation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(PATTERN_NAME, 'w') as f:
            f.write('Test: test')
        cls.boto3_Session = boto3.Session
        cls.cloudformation = type('StubCloudFormation', (), {})()
        cls.clients = {
            'cloudformation': cls.cloudformation
        }
        def client(_, name):
            return cls.clients[name]
        boto3.Session = type('StubSession', (), {
            'client': client
        })

    @classmethod
    def tearDownClass(cls):
        os.remove(PATTERN_NAME)
        boto3.Session = cls.boto3_Session
        client.ClientProxy._session = None

    def setUp(self):
        self.describe_stacks_data = {};
        def describe_stacks(StackName):
            return self.describe_stacks_data[StackName]
        self.cloudformation.describe_stacks = describe_stacks

    def tearDown(self):
        del self.cloudformation.describe_stacks #pylint: disable=E1101

    def test_get_stack_info(self):
        self.describe_stacks_data['stack-1'] = { 'Stacks': [{ 'tag': 'test-stack-1' }] }
        self.assertEqual(cloudformation.get_stack_info('stack-1'), { 'tag': 'test-stack-1' })

    def test_get_sources_bucket(self):
        outputs = [
            { 'OutputKey': 'key-1' },
            { 'OutputKey': SOURCES_BUCKET, 'OutputValue': 'test-bucket-1' },
            { 'OutputKey': 'key-2' }
        ]
        self.describe_stacks_data['stack-1'] = { 'Stacks': [{ 'Outputs': outputs }] }
        self.assertEqual(cloudformation.get_sources_bucket('stack-1'), 'test-bucket-1')
