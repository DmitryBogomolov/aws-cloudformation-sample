import unittest
import boto3    # pylint: disable=import-error
from .. import client

class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boto3_Session = boto3.Session

    @classmethod
    def tearDownClass(cls):
        boto3.Session = cls.boto3_Session

    def test_get_client(self):
        stub = {'tag': 'stub'}
        clients = {
            'tester': stub
        }
        # pylint: disable=too-few-public-methods
        class StubSession:
            def __init__(self, **kwargs):
                self.__class__.args = kwargs

            # pylint: disable=no-self-use
            def client(self, name):
                return clients[name]

        boto3.Session = StubSession
        pattern = {'profile': 'profile-1', 'region': 'region-1'}
        tester = client.get_client(pattern, 'tester')

        self.assertEqual(tester, stub)
        self.assertEqual(StubSession.args,
            {'profile_name': 'profile-1', 'region_name': 'region-1'})
