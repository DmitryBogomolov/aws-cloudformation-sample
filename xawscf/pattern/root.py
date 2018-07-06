from ..utils.const import SOURCES_BUCKET
from ..utils.helper import try_set_field
from .base import Base

def find_by_name(resources, name):
    return next((obj for obj in resources if obj.name == name), None)


class Root(Base):
    TEMPLATE = \
'''
AWSTemplateFormatVersion: 2010-09-09
Resources:
  {0}:
    Type: AWS::S3::Bucket
Outputs:
  {0}:
    Value: !Ref {0}
'''.format(SOURCES_BUCKET)

    RESOURCE_TYPES = {}


    def __init__(self, source):
        super().__init__(source)

        self.resources = []
        self.functions = []
        self.statemachines = []

        for name, obj in self.get('resources', {}).items():
            resource_cls = self.RESOURCE_TYPES[obj['type']]
            resource = resource_cls(name, obj, self)
            self.resources.append(resource)
            if resource.TYPE == 'function':
                self.functions.append(resource)
            elif resource.TYPE == 'statemachine':
                self.statemachines.append(resource)

    def _dump(self, template):
        try_set_field(template, 'Description', self.get('description', None))
        # Have to set it here because it cannot be set in `TEMPLATE` as `TEMPLATE` is used
        # to create stack (before updates) and transfoms are not allowed in CreateStack.
        template['Transform'] = 'AWS::Serverless-2016-10-31'
        template['Resources'].update(self.get('Resources', {}))
        template['Outputs'].update(self.get('Outputs', {}))
        for obj in self.resources:
            obj.dump(template)

    def get_function(self, name):
        return find_by_name(self.functions, name)

    def get_statemachine(self, name):
        return find_by_name(self.statemachines, name)


def register_resource(resource_cls):
    Root.RESOURCE_TYPES[resource_cls.TYPE] = resource_cls
