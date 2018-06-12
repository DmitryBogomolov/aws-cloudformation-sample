import json
from ..utils.yaml import Custom
from ..utils.helper import get_full_name, make_output, try_set_field
from .base_resource import BaseResource
from .role import Role

class StateMachineRole(Role):
    PRINCIPAL_SERVICE = Custom('!Sub', 'states.${AWS::Region}.amazonaws.com')

def get_role_name(name):
    return name + 'Role'

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

        StateMachineRole(get_role_name(name), {
            'statement': self.get('role_statement', [])
        }, self.root).dump(parent_template)

        outputs = parent_template['Outputs']
        outputs[name] = make_output(Custom('!GetAtt', name + '.Name'))
        outputs[name + 'Arn'] = make_output(Custom('!Ref', name))

    def _dump_properties(self, properties):
        properties['StateMachineName'] = self.full_name
        properties['RoleArn'] = Custom('!GetAtt', get_role_name(self.name) + '.Arn')

        definition = self.get('definition')
        if isinstance(definition, dict):
            definition = json.dumps(definition, indent=2)
        properties['DefinitionString'] = {
            'Fn::Sub': [
                definition,
                self.get('definition_args', {})
            ]
        }
