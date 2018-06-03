from .utils import try_set_field
from .base import Base

class Root(Base):
    TEMPLATE = \
'''
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Resources: {}
Outputs: {}
'''

    RESOURCE_TYPES = {}

    def __init__(self, source):
        super().__init__(source)

        self.resources = []
        self.functions = []

        for name, source in self.get('resources', {}).items():
            Resource = self.RESOURCE_TYPES[source['type']]
            resource = Resource(name, source, self)
            self.resources.append(resource)
            if resource.TYPE == 'function':
                self.functions.append(resource)

    def _dump(self, template):
        try_set_field(template, 'Description', self.get('description', ''))
        template['Resources'].update(self.get('Resources', {}))
        template['Outputs'].update(self.get('Outputs', {}))
        for obj in self.resources:
            obj.dump(template)

    def get_function(self, name):
        return next((func for func in self.functions if func.name == name), None)


def register_resource(Resource):
    Root.RESOURCE_TYPES[Resource.TYPE] = Resource
