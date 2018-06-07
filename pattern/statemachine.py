import json
from utils.yaml import Custom
from .utils import get_full_name, make_output, try_set_field
from .base_resource import BaseResource
from .role import Role

class StateMachineRole(Role):
    STATEMENT_TEMPLATE = \
'''
- Effect: Allow
  Action: lambda:InvokeFunction
'''

    PRINCIPAL_SERVICE = Custom('!Sub', 'states.${AWS::Region}.amazonaws.com')

    def _dump_properties(self, properties):
        super()._dump_properties(properties)
        statement = properties['Policies'][0]['PolicyDocument']['Statement'][0]
        statement['Resource'] = [Custom('!GetAtt', name + '.Arn') for name in self.get('functions')]


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

    TYPE = 'statemachine'

    def __init__(self, *args):
        super().__init__(*args)
        self.full_name = get_full_name(self.name, self.root)

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

        # It is done here (not in `_dump_properties`) to pass list of functions to role.
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
        properties['StateMachineName'] = self.full_name
        properties['RoleArn'] = Custom('!GetAtt', get_role_name(self.name) + '.Arn')
