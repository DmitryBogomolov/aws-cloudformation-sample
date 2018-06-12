from ..utils import helper
from ..utils.yaml import Custom
from ..utils.const import SOURCES_BUCKET
from .utils import get_full_name, try_set_field, make_output
from .base_resource import BaseResource

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
Properties: {}
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        template['DependsOn'].append(self.get('function'))

    def _dump_properties(self, properties):
       properties['FunctionName'] = Custom('!Ref', self.get('function'))


class Function(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Serverless::Function
Properties:
  Environment:
    Variables: {}
  Tags: {}
'''

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
        LogGroup(log_name, { 'group_name': self.log_group_name }, self.root).dump(parent_template)
        LambdaVersion(version_name, { 'function': name }, self.root).dump(parent_template)

        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][version_name] = make_output(Custom('!Ref', version_name))

        template['DependsOn'].append(log_name)

    def _dump_properties(self, properties):
        properties['FunctionName'] = self.full_name
        properties['Handler'] = self.get('handler')
        properties['CodeUri'] = {
            'Bucket': Custom('!Ref', SOURCES_BUCKET),
            'Key': helper.get_archive_name(self.get('code_uri'))
        }
        try_set_field(properties, 'Description', self.get('description', ''))
        try_set_field(properties, 'Runtime',
            self.get('runtime', '') or self.root.get('function_runtime', ''))
        try_set_field(properties, 'Timeout',
            self.get('timeout', '') or self.root.get('function_timeout', ''))
        try_set_field(properties, 'Role', self.get('role', ''))
        properties['Tags'].update(self.get('tags', {}))
        properties['Environment']['Variables'].update(self.get('environment', {}))
        if len(properties['Environment']['Variables']) == 0:
            properties.pop('Environment')
