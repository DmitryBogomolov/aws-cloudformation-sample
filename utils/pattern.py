import yaml
from . import helper
from .yaml import load, Custom

class Base(object):
    def __init__(self, source):
        self._source = source

    def get(self, name):
        return self._source[name]

    def try_get(self, name):
        return self._source.get(name)

    def get_map(self, name):
        return self._source.get(name, {})

    def get_list(self, name):
        return self._source.get(name, [])

    def dump(self):
        resource = yaml.load(self.TEMPLATE)
        self._dump(resource)
        return resource


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
        self.outputs = []
        self.functions = []

    def init(self):
        for name, source in self.get_map('resources').items():
            Resource = self.RESOURCE_TYPES[source['type']]
            resource = Resource(source, name, self)
            resources, outputs = resource.init()
            self.resources.append(resource)
            self.resources.extend(resources)
            self.outputs.extend(outputs)
            if isinstance(resource, Function):
                self.functions.append(resource)

    def _dump(self, template):
        template['Description'] = self.try_get('description')
        resources = template['Resources']
        resources.update(self.get_map('Resources'))
        for obj in self.resources:
            resources[obj.name] = obj.dump()
        outputs = template['Outputs']
        outputs.update(self.get_map('Outputs'))
        for obj in self.outputs:
            outputs[obj.name] = obj.dump()

    def get_function(self, name):
        return next((func for func in self.functions if func.name == name), None)


def try_set_field(target, name, value):
    if value:
        target[name] = value


class BaseResource(Base):
    def __init__(self, source, name, root):
        super().__init__(source)
        self.name = name
        self.root = root

    def _dump(self, template):
        properties = template['Properties']
        properties.update(self.get_map('Properties'))
        self._dump_properties(properties)


class Function(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Serverless::Function
Properties:
  Environment:
    Variables: {}
  Tags: {}
DependsOn: []
'''

    def __init__(self, source, name, root):
        super().__init__(source, name, root)
        self.full_name = root.get('project') + '-' + name

    def init(self):
        name = self.name

        self.log_group = LogGroup(name, self.full_name)
        self.version = LambdaVersion(name)

        output_name = Output(name, Custom('!Ref', name))
        output_version = Output(self.version.name, Custom('!Ref', self.version.name))

        return [self.log_group, self.version], [output_name, output_version]

    def _dump(self, template):
        super()._dump(template)
        template['DependsOn'].append(self.log_group.name)
        template['DependsOn'].extend(self.get_list('depends_on'))

    def _dump_properties(self, properties):
        properties['FunctionName'] = self.full_name
        properties['Handler'] = self.get('handler')
        properties['CodeUri'] = 's3://{}/{}/{}'.format(
            self.root.get('bucket'),
            self.root.get('project'),
            helper.get_archive_name(self.get('code_uri'))
        )
        try_set_field(properties, 'Description', self.try_get('description'))
        try_set_field(properties, 'Runtime',
            self.try_get('runtime') or self.root.try_get('function_runtime'))
        try_set_field(properties, 'Timeout',
            self.try_get('timeout') or self.root.try_get('function_timeout'))
        try_set_field(properties, 'Role', self.try_get('role'))
        properties['Tags'].update(self.get_map('tags'))
        properties['Environment']['Variables'].update(self.get_map('environment'))
        if len(properties['Environment']['Variables']) == 0:
            properties.pop('Environment')


Root.RESOURCE_TYPES['function'] = Function


class Policy(Base):
    TEMPLATE = \
'''
PolicyName: <PolicyName>
PolicyDocument:
  Version: 2012-10-17
  Statement: []
'''

    def __init__(self, name, statement):
        super().__init__(None)
        self.name = name
        self.statement = statement

    def _dump(self, template):
        template['PolicyName'] = self.name
        template['PolicyDocument']['Statement'].extend(self.statement)


class LambdaRole(BaseResource):
    TEMPLATE = \
'''
Type: AWS::IAM::Role
Properties:
  AssumeRolePolicyDocument:
    Version: 2012-10-17
    Statement:
      - Effect: Allow
        Principal:
          Service: lambda.amazonaws.com
        Action: sts:AssumeRole
  Path: /
  ManagedPolicyArns:
    - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
  Policies: []
'''

    def init(self):
        return [], []

    def _dump_properties(self, properties):
        properties['RoleName'] = Custom('!Sub',
            self.root.get('project') + '-${AWS::Region}-' + self.name)
        policies = [Policy(**policy).dump() for policy in self.get_list('policies')]
        properties['Policies'].extend(policies)


Root.RESOURCE_TYPES['lambda-role'] = LambdaRole


class LogGroup(Base):
    TEMPLATE = \
'''
Type: AWS::Logs::LogGroup
Properties: {}
'''

    def __init__(self, name, lambda_name):
        super().__init__(None)
        self.name = name + 'LogGroup'
        self.group_name = '/aws/lambda/' + lambda_name

    def _dump(self, template):
        template['Properties']['LogGroupName'] = self.group_name


class LambdaVersion(Base):
    TEMPLATE = \
'''
Type: AWS::Lambda::Version
Properties: {}
'''

    def __init__(self, name):
        super().__init__(None)
        self.name = name + 'Version'
        self.function_name = name

    def _dump(self, template):
       template['Properties']['FunctionName'] = Custom('!Ref', self.function_name)


class S3Bucket(BaseResource):
    TEMPLATE = \
'''
Type: AWS::S3::Bucket
Properties:
  Tags: []
'''

    def __init__(self, source, name, root):
        super().__init__(source, name, root)

        self.output_name = Output(name, Custom('!Ref', name))
        self.output_url = Output(name + 'Url', Custom('!GetAtt', name + '.WebsiteURL'))

    def init(self):
        name = self.name

        output_name = Output(name, Custom('!Ref', name))
        output_url = Output(name + 'Url', Custom('!GetAtt', name + '.WebsiteURL'))

        return [], [output_name, output_url]

    def _dump_properties(self, properties):
        tags = [{ 'Key': key, 'Value': value } for key, value in self.get_map('tags').items()]
        properties['Tags'].extend(tags)


Root.RESOURCE_TYPES['bucket'] = S3Bucket


class Output(Base):
    TEMPLATE = '{}'

    def __init__(self, name, value):
        super().__init__(None)
        self.name = name
        self.value = value

    def _dump(self, template):
        template['Value'] = self.value


def check_required_fields(source):
    absent = []
    for field in ('project', 'bucket'):
        if not source.get(field):
            absent.append(field)
    if len(absent) > 0:
        raise Exception('The following fields are not defined: {}'.format(', '.join(absent)))

def create_pattern():
    source = load(helper.get_pattern_path())
    check_required_fields(source)
    root = Root(source)
    root.init()
    return root

pattern = create_pattern()
