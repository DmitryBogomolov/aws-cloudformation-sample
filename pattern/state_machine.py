from utils.yaml import Custom
from .utils import try_set_field, make_output
from .base_resource import BaseResource

class StateMachine(BaseResource):
    TEMPLATE = \
'''
Type: AWS::StepFunctions::StateMachine
Properties:
  StateMachineName: String
  DefinitionString: String
  RoleArn: String
'''

    TYPE = 'state-machine'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        outputs = parent_template['Outputs']
        outputs[name] = make_output(Custom('!GetAtt', name + '.Name'))
        outputs[name + 'Arn'] = make_output(Custom('!Ref', name))

    def _dump_properties(self, properties):
        try_set_field(properties, 'StateMachineName', self.get('name', ''))
