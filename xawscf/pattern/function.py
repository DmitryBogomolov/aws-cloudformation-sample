from ..utils import helper
from ..utils.loader import Custom
from ..utils.const import SOURCES_BUCKET
from ..utils.helper import get_full_name, try_set_field, make_output
from .base_resource import BaseResource
from .role import Role

class LogGroup(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Logs::LogGroup
Properties: {}
'''

    def _dump_properties(self, properties):
        properties['LogGroupName'] = self.get('group_name')


class LambdaVersion(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Lambda::Version
Properties:
  FunctionName: !Ref null
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        template['DependsOn'].append(self.get('function'))

    def _dump_properties(self, properties):
        properties['FunctionName'].value = self.get('function')


class FunctionRole(Role):
    PRINCIPAL_SERVICE = 'lambda.amazonaws.com'
    MANAGED_POLICIES = ['arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole']


class Function(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Serverless::Function
Properties:
  CodeUri:
    Bucket: !Ref {}
  Environment:
    Variables: {{}}
  Tags: {{}}
'''.format(SOURCES_BUCKET)

    TYPE = 'function'

    def __init__(self, *args):
        super().__init__(*args)
        self.full_name = get_full_name(self.name, self.root)
        self.log_group_name = '/aws/lambda/' + self.full_name

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)

        name = self.name
        log_name = name + 'LogGroup'
        version_name = name + 'Version'
        LogGroup(log_name, {'group_name': self.log_group_name}, self.root).dump(parent_template)
        LambdaVersion(version_name, {'function': name}, self.root).dump(parent_template)

        role_statement = self.get('role_statement', None)
        if role_statement:
            role_name = name + 'Role'
            FunctionRole(role_name, {
                'statement': role_statement,
                'depends_on': self.get('depends_on', None)
            }, self.root).dump(parent_template)
            template['Properties']['Role'] = Custom('!GetAtt', role_name + '.Arn')
            template['DependsOn'].append(role_name)

        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][version_name] = make_output(Custom('!Ref', version_name))

        template['DependsOn'].append(log_name)

    def _dump_properties(self, properties):
        properties['FunctionName'] = self.full_name
        properties['Handler'] = self.get('handler')
        properties['CodeUri']['Key'] = helper.get_archive_name(self.get('code_uri'))
        try_set_field(properties, 'Description', self.get('description', None))
        # TODO: Some runtime and timeout must eventually be set - now it is possible to have none.
        try_set_field(properties, 'Runtime',
            self.get('runtime', None) or self.root.get('function_runtime', None))
        try_set_field(properties, 'Timeout',
            self.get('timeout', None) or self.root.get('function_timeout', None))
        try_set_field(properties, 'Role',
            self.get('role', None) if not self.get('role_statement', None) else None)
        properties['Tags'].update(self.get('tags', {}))
        properties['Environment']['Variables'].update(self.get('environment', {}))
        if not properties['Environment']['Variables']:
            properties.pop('Environment')
