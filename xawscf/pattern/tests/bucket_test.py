import unittest
from .. import bucket
from ...utils.loader import Custom

class TestBucket(unittest.TestCase):
    # pylint: disable=invalid-name
    def test_dump_Bucket(self):
        resources = {}
        outputs = {}
        obj = bucket.Bucket('Bucket1', {

        }, None)
        obj.dump({'Resources': resources, 'Outputs': outputs})

        self.assertEqual(resources, {
            'Bucket1': {
                'Type': 'AWS::S3::Bucket',
                'Properties': {'Tags': []},
                'DependsOn': []
            }
        })
        self.assertEqual(outputs, {
            'Bucket1': {'Value': Custom('!Ref', 'Bucket1')},
            'Bucket1Url': {'Value': Custom('!GetAtt', 'Bucket1.WebsiteURL')}
        })
