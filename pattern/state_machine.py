import json
from utils.yaml import Custom
from .utils import make_output, try_set_field
from .base_resource import BaseResource

class StateMachineRole(BaseResource):
    TEMPLATE = \
'''
Type: AWS::IAM::Role
Properties:
  AssumeRolePolicyDocument:
    Version: 2012-10-17
    Statement:
      - Effect: Allow
        Principal:
          Service: !Sub states.${AWS::Region}.amazonaws.com
        Action: sts:AssumeRole
  Path: '/'
  Policies:
    - PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action: lambda:InvokeFunction
            Resource: '*'
'''

    def _dump_properties(self, properties):
        properties['Policies'][0]['PolicyName'] = self.name + 'Policy'
        properties['Policies'][0]['PolicyDocument']['Statement'][0]['Resource'] = [
            Custom('!GetAtt', name + '.Arn') for name in self.get('functions')]


def get_role_name(name):
    return name + 'Role'

def patch_state_resources(states, functions, args):
    for state in states.values():
        if state['Type'] == 'Task':
            function = state['Resource']
            state['Resource'] = '${' + function + '}'
            args[function] = Custom('!GetAtt', function + '.Arn')
            functions.add(function)
        elif state['Type'] == 'Parallel':
            for branch in state['Branches']:
                patch_state_resources(branch['States'], functions, args)


class StateMachine(BaseResource):
    TEMPLATE = \
'''
Type: AWS::StepFunctions::StateMachine
Properties: {}
'''

    TYPE = 'state-machine'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name

        states = self.get('states')
        functions = set()
        args = {}
        patch_state_resources(states, functions, args)
        definition = {
            'StartAt': self.get('start_at'),
            'States': states
        }
        try_set_field(definition, 'Comment', self.get('comment', ''))

        template['Properties']['DefinitionString'] = {
            'Fn::Sub': [
                json.dumps(definition, indent=2),
                args
            ]
        }

        StateMachineRole(get_role_name(name), {
            'functions': list(functions)
        }, self.root).dump(parent_template)

        outputs = parent_template['Outputs']
        outputs[name] = make_output(Custom('!GetAtt', name + '.Name'))
        outputs[name + 'Arn'] = make_output(Custom('!Ref', name))

    def _dump_properties(self, properties):
        properties['StateMachineName'] = self.root.get('project') + '-' + self.name
        properties['RoleArn'] = Custom('!GetAtt', get_role_name(self.name) + '.Arn')
