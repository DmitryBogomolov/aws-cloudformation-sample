import unittest
from .. import function
from ...utils.yaml import Custom

class TestFunction(unittest.TestCase):
    def test_dump_LogGroup(self):
        resources = {}
        obj = function.LogGroup('Group1', {
            'group_name': 'group-1'
        }, None)
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources, {
            'Group1': {
                'Type': 'AWS::Logs::LogGroup',
                'Properties': {
                    'LogGroupName': 'group-1'
                },
                'DependsOn': []
            }
        })

    def test_dump_LambdaVersion(self):
        resources = {}
        obj = function.LambdaVersion('Version1', {
            'function': 'Function1'
        }, None)
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources, {
            'Version1': {
                'Type': 'AWS::Lambda::Version',
                'Properties': {
                    'FunctionName': Custom('!Ref', 'Function1')
                },
                'DependsOn': ['Function1']
            }
        })

    def test_dump_Function(self):
        self.maxDiff = None
        resources = {}
        outputs = {}
        obj = function.Function('Function1', {
            'description': 'This is function',
            'handler': 'index.handler',
            'code_uri': 'index.py',
            'runtime': 'python3',
            'timeout': 2,
            'tags': {
                'tag-1': 10,
                'tag-2': 20
            },
            'environment': {
                'a': 1,
                'b': 2
            }
        }, { 'project': 'project1' })
        obj.dump({ 'Resources': resources, 'Outputs': outputs })

        self.assertEqual(obj.name, 'Function1')
        self.assertEqual(obj.full_name, 'project1-Function1')
        self.assertEqual(len(resources), 3)
        self.assertEqual(resources['Function1'], {
            'Type': 'AWS::Serverless::Function',
            'Properties': {
                'FunctionName': 'project1-Function1',
                'Description': 'This is function',
                'Handler': 'index.handler',
                'CodeUri': {
                    'Bucket': Custom('!Ref', 'SourcesBucket'),
                    'Key': 'index_py.zip'
                },
                'Runtime': 'python3',
                'Timeout': 2,
                'Tags': { 'tag-1': 10, 'tag-2': 20 },
                'Environment': {
                    'Variables': { 'a': 1, 'b': 2 }
                }
            },
            'DependsOn': ['Function1LogGroup']
        })
        self.assertIsNotNone(resources['Function1LogGroup'])
        self.assertIsNotNone(resources['Function1Version'])
        self.assertEqual(outputs, {
            'Function1': { 'Value': Custom('!Ref', 'Function1') },
            'Function1Version': { 'Value': Custom('!Ref', 'Function1Version') }
        })
