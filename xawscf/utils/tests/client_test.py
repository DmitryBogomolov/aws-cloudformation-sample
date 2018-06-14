import unittest
import boto3
import os
from ..helper import PATTERN_NAME
from .. import client

class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boto3_Session = boto3.Session

    @classmethod
    def tearDownClass(cls):
        boto3.Session = cls.boto3_Session

    def test_real_client_is_not_created_until_method_call(self):
        tester = client.client('tester')
        self.assertTrue(tester)

    def test_real_client_is_created_on_method_call(self):
        def do_test(self):
            stub.called = True
        stub = type('StubTester', (), { 'called': False, 'do_test': do_test })()
        clients = {
            'tester': stub
        }
        boto3.Session = type('StubSession', (), {
            'client': lambda _, name: clients[name]
        })
        with open(PATTERN_NAME, 'w') as f:
            f.write('Test: test')
        try:
            tester = client.client('tester')
            tester.do_test()
            self.assertTrue(stub.called)
        finally:
            os.remove(PATTERN_NAME)

    def test_proxies_are_reused(self):
        tester1 = client.client('tester-a')
        tester2 = client.client('tester-a')
        tester3 = client.client('tester-b')
        self.assertEqual(tester1, tester2)
        self.assertNotEqual(tester1, tester3)
