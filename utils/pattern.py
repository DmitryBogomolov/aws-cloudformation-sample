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

    def __init__(self, source):
        super().__init__(source)

        self.resources = []
        self.outputs = []
        self.functions = []

    def _dump(self, template):
        template['Description'] = self.try_get('description')
        template['Resources'].update(self.get_map('Resources'))
        resources = { obj.name: obj.dump() for obj in self.resources }
        template['Resources'].update(resources)
        template['Outputs'].update(self.get_map('Outputs'))
        outputs = { obj.name: obj.dump() for obj in self.outputs }
        template['Outputs'].update(outputs)

    def get_function(self, name):
        return next((func for func in self.functions if func.name == name), None)


def try_set_field(target, name, value):
    if value:
        target[name] = value


class Function(Base):
    TEMPLATE = \
'''
Type: AWS::Serverless::Function
Properties:
  Environment:
    Variables: {}
  Tags: {}
DependsOn: []
'''

    def __init__(self, name, source, root):
        super().__init__(source)
        self.root = root
        self.name = name
        self.full_name = root.get('project') + '-' + name

        self.log_group = LogGroup(name, self.full_name)
        self.version = LambdaVersion(name)

        self.output_name = Output(name, Custom('!Ref', name))
        self.output_version = Output(self.version.name, Custom('!Ref', self.version.name))

    def _dump(self, resource):
        properties = resource['Properties']
        properties.update(self.get_map('Properties'))
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
        resource['DependsOn'].append(self.log_group.name)
        resource['DependsOn'].extend(self.get_list('depends_on'))


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

    def _dump(self, resource):
        resource['PolicyName'] = self.name
        resource['PolicyDocument']['Statement'].extend(self.statement)


class LambdaRole(Base):
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

    def __init__(self, name, source, root):
        super().__init__(source)
        self.root = root
        self.name = name

    def _dump(self, resource):
        properties = resource['Properties']
        properties.update(self.get_map('Properties'))
        properties['RoleName'] = Custom('!Sub',
            self.root.get('project') + '-${AWS::Region}-' + self.name)
        policies = [Policy(**policy).dump() for policy in self.get_list('policies')]
        properties['Policies'].extend(policies)


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

    def _dump(self, resource):
        properties = resource['Properties']
        properties['LogGroupName'] = self.group_name


class LambdaVersion(Base):
    TEMPLATE = \
'''
Type: AWS::Lambda::Version
Properties: {}
'''

    def __init__(self, name):
        super().__init__(None)
        self.name = name + 'Version'

    def _dump(self, resource):
       resource['Properties']['FunctionName'] = Custom('!Ref', self.name)


class S3Bucket(Base):
    TEMPLATE = \
'''
Type: AWS::S3::Bucket
Properties:
  Tags: []
'''

    def __init__(self, name, source, root):
        super().__init__(source)
        self.root = root
        self.name = name

        self.output_name = Output(name, Custom('!Ref', name))
        self.output_url = Output(name + 'Url', Custom('!GetAtt', name + '.WebsiteURL'))

    def _dump(self, resource):
        properties = resource['Properties']
        properties.update(self.get_map('Properties'))
        tags = [{ 'Key': key, 'Value': value } for key, value in self.get_map('tags').items()]
        properties['Tags'].extend(tags)


class Output(Base):
    TEMPLATE = \
'''
Value: null
'''

    def __init__(self, name, value):
        super().__init__(None)
        self.name = name
        self.value = value

    def _dump(self, resource):
        resource['Value'] = self.value


def check_required_fields(source):
    absent = []
    for field in ('project', 'bucket'):
        if not source.get(field):
            absent.append(field)
    if len(absent) > 0:
        raise Exception('The following fields are not defined: {}'.format(', '.join(absent)))

def process_resources(pattern, source):
    for name, resource in source.items():
        resource_type = resource['type']
        if resource_type == 'function':
            function = Function(name, resource, pattern)
            pattern.functions.append(function)
            pattern.resources.append(function.log_group)
            pattern.resources.append(function)
            pattern.resources.append(function.version)
            pattern.outputs.append(function.output_name)
            pattern.outputs.append(function.output_version)
        elif resource_type == 'lambda-role':
            role = LambdaRole(name, resource, pattern)
            pattern.resources.append(role)
        elif resource_type == 'bucket':
            bucket = S3Bucket(name, resource, pattern)
            pattern.resources.append(bucket)
            pattern.outputs.append(bucket.output_name)
            pattern.outputs.append(bucket.output_url)

def create_pattern():
    source = load(helper.get_pattern_path())
    check_required_fields(source)
    root = Root(source)
    process_resources(root, source.get('resources', {}))
    return root

pattern = create_pattern()
