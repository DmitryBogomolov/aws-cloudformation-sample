import unittest
import json
from datetime import date
from .. import statemachine
from ...utils.loader import Custom

class TestStateMachine(unittest.TestCase):
    # pylint: disable=invalid-name
    def test_dump_StateMachineRole(self):
        self.maxDiff = None
        resources = {}
        obj = statemachine.StateMachineRole('Role1', {}, {'project': 'project1'})
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
                            'Principal': {
                                'Service': Custom('!Sub', 'states.${AWS::Region}.amazonaws.com')
                            }
                        }]
                    },
                    'Path': '/',
                    'RoleName': Custom('!Sub', 'project1-${AWS::Region}-Role1'),
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

    # pylint: disable=invalid-name
    def test_dump_StateMachine(self):
        self.maxDiff = None
        resources = {}
        outputs = {}
        obj = statemachine.StateMachine('StateMachine1', {
            'definition': {
                'state-1': 1,
                'state-2': 2
            },
            'definition_args': {'a': 1, 'b': 2},
            'role_statement': ['role-statement-1']
        }, {'project': 'project1'})
        obj.dump({'Resources': resources, 'Outputs': outputs})

        self.assertEqual(obj.name, 'StateMachine1')
        self.assertEqual(obj.full_name, 'project1-StateMachine1')
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources['StateMachine1'], {
            'Type': 'AWS::StepFunctions::StateMachine',
            'Properties': {
                'StateMachineName': 'project1-StateMachine1',
                'RoleArn': Custom('!GetAtt', 'StateMachine1Role.Arn'),
                'DefinitionString': Custom('!Sub', [
                    json.dumps({'state-1': 1, 'state-2': 2}, indent=2),
                    {'a': 1, 'b': 2}
                ])
            },
            'DependsOn': ['StateMachine1Role']
        })
        self.assertEqual(resources['StateMachine1Role']['Properties']
            ['Policies'][0]['PolicyDocument']['Statement'], ['role-statement-1'])
