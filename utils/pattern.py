import yaml
from . import helper
from .yaml import load, Custom

def take_dict(source, field):
    return source.get(field) or {}


class Base(object):
    def dump(self):
        resource = yaml.load(self.TEMPLATE)
        self._dump(resource)
        return resource


class Root(Base):
    TEMPLATE = \
'''
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Description: <Description>
Resources: {}
Outputs: {}
'''

    def __init__(self, source):
        self.Resources = take_dict(source, 'Resources')
        self.Outputs = take_dict(source, 'Outputs')
        self.project = source['project']
        self.bucket = source['bucket']
        self.description = source.get('description')
        self.profile = source.get('profile')
        self.region = source.get('region')
        self.function_timeout = source.get('function_timeout')
        self.function_runtime = source.get('function_runtime')
        self.resources = []
        self.functions = []
        self.outputs = []

    def _dump(self, resource):
        resource['Description'] = self.description
        resource['Resources'].update(self.Resources)
        resources = { obj.name: obj.dump() for obj in self.resources }
        resource['Resources'].update(resources)
        resource['Outputs'].update(self.Outputs)
        outputs = { obj.name: obj.dump() for obj in self.outputs }
        resource['Outputs'].update(outputs)


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
        self.root = root
        self.name = name
        self.Properties = take_dict(source, 'Properties')

        self.description = source.get('description')
        self.full_name = helper.get_function_name(root, name)
        self.handler = source['handler']
        self.code_uri = source['code_uri']
        self.tags = take_dict(source, 'tags')
        self.timeout = source.get('timeout') or root.function_timeout
        self.runtime = source.get('runtime') or root.function_runtime
        self.role = source.get('role')
        self.environment = take_dict(source, 'environment')
        self.depends_on = source.get('depends_on') or []

        self.log_group = LogGroup(name, root)
        self.version = LambdaVersion(name)

        self.output_name = Output(name, Custom('!Ref', name))
        self.output_version = Output(self.version.name, Custom('!Ref', self.version.name))

    def _dump(self, resource):
        properties = resource['Properties']
        properties.update(self.Properties)
        properties.update(
            FunctionName=self.full_name,
            Description=self.description,
            Runtime=self.runtime,
            Timeout=self.timeout,
            Tags=self.tags,
            Handler=self.handler,
            Role=self.role,
            CodeUri='s3://{}/{}/{}'.format(
                self.root.bucket, self.root.project, helper.get_archive_name(self.code_uri))
        )
        properties['Environment']['Variables'].update(self.environment)
        resource['DependsOn'].append(self.log_group.name)
        resource['DependsOn'].extend(self.depends_on)


class Policy(Base):
    TEMPLATE = \
'''
PolicyName: <PolicyName>
PolicyDocument:
  Version: 2012-10-17
  Statement: []
'''

    def __init__(self, name, statement):
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
        self.root = root
        self.name = name
        self.Properties = take_dict(source, 'Properties')

        self.policies = [Policy(**obj) for obj in source['policies']]

    def _dump(self, resource):
        properties = resource['Properties']
        properties.update(self.Properties)
        policies = [policy.dump() for policy in self.policies]
        properties['Policies'].extend(policies)


class LogGroup(Base):
    TEMPLATE = \
'''
Type: AWS::Logs::LogGroup
Properties:
  LogGroupName: <LogGroupName>
'''

    def __init__(self, name, root):
        self.name = name + 'LogGroup'
        self.group_name = helper.get_log_group_name(root, name)

    def _dump(self, resource):
        resource['Properties']['LogGroupName'] = self.group_name


class LambdaVersion(Base):
    TEMPLATE = \
'''
Type: AWS::Lambda::Version
Properties:
  FunctionName: <FunctionName> 
'''

    def __init__(self, name):
        self.name = name + 'Version'
        self.function_name = Custom('!Ref', name)

    def _dump(self, resource):
       resource['Properties']['FunctionName'] = self.function_name


class Output(Base):
    TEMPLATE = \
'''
Value: <Value>
'''

    def __init__(self, name, value):
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
        if resource['type'] == 'function':
            function = Function(name, resource, pattern)
            pattern.functions.append(function)
            pattern.resources.append(function.log_group)
            pattern.resources.append(function)
            pattern.resources.append(function.version)
            pattern.outputs.append(function.output_name)
            pattern.outputs.append(function.output_version)
        elif resource['type'] == 'lambda-role':
            role = LambdaRole(name, resource, pattern)
            pattern.resources.append(role)

def create_pattern():
    source = load(helper.get_pattern_path())
    check_required_fields(source)
    root = Root(source)
    process_resources(root, take_dict(source, 'resources'))
    return root

pattern = create_pattern()
