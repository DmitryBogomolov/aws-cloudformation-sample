import unittest
from datetime import date
from .. import function_role
from ...utils.yaml import Custom

class TestFunctionRole(unittest.TestCase):
    def test_dump_FunctionRole(self):
        self.maxDiff = None
        resources = {}
        obj = function_role.FunctionRole('Role1', {}, { 'project': 'project-1' })
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources, {
            'Role1': {
                'Type': 'AWS::IAM::Role',
                'Properties': {
                    'AssumeRolePolicyDocument': {
                        'Version': date(2012, 10, 17),
                        'Statement': [{
                            'Effect': 'Allow',
                            'Action': 'sts:AssumeRole',
                            'Principal': { 'Service': 'lambda.amazonaws.com' }
                        }]
                    },
                    'Path': '/',
                    'ManagedPolicyArns': ['arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'],
                    'RoleName': Custom('!Sub', 'project-1-${AWS::Region}-Role1'),
                    'Policies': [{
                        'PolicyName': 'Role1Policy',
                        'PolicyDocument': {
                            'Version': date(2012, 10, 17),
                            'Statement': []
                        }
                    }]
                },
                'DependsOn': []
            }
        })
