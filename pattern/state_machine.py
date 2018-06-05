import json
from utils.yaml import Custom
from .utils import make_output
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

def build_definition(states, start_at, comment):
    pass


class StateMachine(BaseResource):
    TEMPLATE = \
'''
Type: AWS::StepFunctions::StateMachine
Properties:
  DefinitionString:
    Fn::Sub:
      - |-
        {
          "Comment": "This is a comment",
          "StartAt": "state-1",
          "States": {
            "state-1": {
              "Type": "Task",
              "Resource": "${DoStateAction}",
              "Next": "end"
            },
            "end": {
              "Type": "Pass",
              "End": true
            }
          }
        }
      - { DoStateAction: !GetAtt DoStateAction.Arn }
'''

    TYPE = 'state-machine'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name

        states = {}
        functions = set()
        args = {}
        for state_name, state in self.get('states').items():
            if state['Type'] == 'Task':
                function = state['Resource']
                state['Resource'] = '${' + function + '}'
                args[function] = Custom('!GetAtt', function + '.Arn')
                functions.add(function)
            states[state_name] = state
        definition = {
            'Comment': self.get('comment'),
            'StartAt': self.get('start_at'),
            'States': states
        }

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
