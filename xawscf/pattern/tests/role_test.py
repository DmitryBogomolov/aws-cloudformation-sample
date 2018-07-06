import unittest
from datetime import date
from .. import role
from ...utils.loader import Custom

class TestRole(unittest.TestCase):
    # pylint: disable=invalid-name
    def test_dump_Role(self):
        self.maxDiff = None
        resources = {}
        obj = role.Role('Role1', {
            'statement': ['s1', 's2']
        }, {'project': 'project-1'})
        obj.PRINCIPAL_SERVICE = 'principal-1'
        obj.MANAGED_POLICIES = ['managed-1']
        obj.STATEMENT_TEMPLATE = '[1]'
        obj.dump({'Resources': resources})

        self.assertEqual(resources, {
            'Role1': {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': date(2012, 10, 17),
                        'Statement': [{
                            'Effect': 'Allow',
                            'Action': 'sts:AssumeRole',
                            'Principal': {'Service': 'principal-1'}
                        }]
                    },
                    'Path': '/',
                    'ManagedPolicyArns': ['managed-1'],
                    'RoleName': Custom('!Sub', 'project-1-${AWS::Region}-Role1'),
                    'Policies': [{
                        'PolicyName': 'Role1Policy',
                        'PolicyDocument': {
                            'Version': date(2012, 10, 17),
                            'Statement': [1, 's1', 's2']
                        }
                    }]
                },
                'DependsOn': []
            }
        })
