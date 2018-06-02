import yaml
from . import helper
from .yaml import load, Custom

class Base(object):
    TEMPLATE = None

    def __init__(self, source):
        self._source = source

    def get(self, name, default=None):
        value = self._source.get(name, default)
        if value is None:
            raise Exception('Field "{}" is not defined.'.format(name))
        return value

    def get_path(self, name):
        obj = self._source
        for item in name.split('.'):
            obj = obj.get(item)
        return obj

    def dump(self):
        template = yaml.load(self.TEMPLATE)
        self._dump(template)
        return template

    def _dump(self, template):
        raise Exception('Abstract')


def try_set_field(target, name, value):
    if value:
        target[name] = value


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
            if isinstance(resource, Function):
                self.functions.append(resource)

    def _dump(self, template):
        try_set_field(template, 'Description', self.get('description', ''))
        template['Resources'].update(self.get('Resources', {}))
        template['Outputs'].update(self.get('Outputs', {}))
        for obj in self.resources:
            obj.dump(template)

    def get_function(self, name):
        return next((func for func in self.functions if func.name == name), None)


class BaseResource(Base):
    def __init__(self, name, source, root):
        super().__init__(source)
        self.name = name
        self.root = root

    def dump(self, parent_template):
        template = yaml.load(self.TEMPLATE)
        self._dump(template, parent_template)
        parent_template['Resources'][self.name] = template

    def _dump(self, template, parent_template):
        properties = template['Properties']
        properties.update(self.get('Properties', {}))
        self._dump_properties(properties)

    def _dump_properties(self, properties):
        raise Exception('Not implemented')


def set_depends_on(template, resource):
    template['DependsOn'].extend(resource.get('depends_on', []))

def make_output(value):
    return { 'Value': value }


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

    def __init__(self, *args):
        super().__init__(*args)
        self.full_name = self.root.get('project') + '-' + self.name

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)

        name = self.name
        log_group = LogGroup(name, self.full_name)
        version = LambdaVersion(name)
        parent_template['Resources'][log_group.name] = log_group.dump()
        parent_template['Resources'][version.name] = version.dump()
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][version.name] = make_output(Custom('!Ref', version.name))

        template['DependsOn'].append(log_group.name)
        set_depends_on(template, self)

    def _dump_properties(self, properties):
        properties['FunctionName'] = self.full_name
        properties['Handler'] = self.get('handler')
        properties['CodeUri'] = 's3://{}/{}/{}'.format(
            self.root.get('bucket'),
            self.root.get('project'),
            helper.get_archive_name(self.get('code_uri'))
        )
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


Root.RESOURCE_TYPES['function'] = Function


class Policy(Base):
    TEMPLATE = \
'''
PolicyName: <PolicyName>
PolicyDocument:
  Version: 2012-10-17
  Statement: []
'''

    def _dump(self, template):
        template['PolicyName'] = self.get('name')
        template['PolicyDocument']['Statement'].extend(self.get('statement', []))


def set_sub_list(target, resource, field, SubResouce):
    target.extend([SubResouce(obj).dump() for obj in resource.get(field, [])])


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
DependsOn: []
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        set_depends_on(template, self)

    def _dump_properties(self, properties):
        properties['RoleName'] = Custom('!Sub',
            self.root.get('project') + '-${AWS::Region}-' + self.name)
        set_sub_list(properties['Policies'], self, 'policies', Policy)


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


def set_tags_list(template, resource):
    tags = [{ 'Key': key, 'Value': value } for key, value in resource.get('tags', {}).items()]
    template['Tags'].extend(tags)


class S3Bucket(BaseResource):
    TEMPLATE = \
'''
Type: AWS::S3::Bucket
Properties:
  Tags: []
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][name + 'Url'] = make_output(
            Custom('!GetAtt', name + '.WebsiteURL'))

    def _dump_properties(self, properties):
        set_tags_list(properties, self)


Root.RESOURCE_TYPES['bucket'] = S3Bucket


def take_pair(obj):
    return list(obj.items())[0]

def set_key_schema(template, resource):
    for obj in resource.get('key_schema', []):
        name, value = take_pair(obj)
        template['KeySchema'].append({
            'AttributeName': name,
            'KeyType': value
        })

def set_throughput(template, resource):
    try_set_field(template['ProvisionedThroughput'], 'ReadCapacityUnits',
        resource.get_path('provisioned_throughput.read_capacity_units'))
    try_set_field(template['ProvisionedThroughput'], 'WriteCapacityUnits',
        resource.get_path('provisioned_throughput.write_capacity_units'))

class LocalSecondaryIndex(Base):
    TEMPLATE = \
'''
KeySchema: []
Projection: {}
'''

    def _dump(self, template):
        template['IndexName'] = self.get('index_name')
        set_key_schema(template, self)
        try_set_field(template['Projection'], 'ProjectionType',
            self.get_path('projection.projection_type'))


class GlobalSecondaryIndex(LocalSecondaryIndex):
    TEMPLATE = LocalSecondaryIndex.TEMPLATE + \
'''
ProvisionedThroughput: {}
'''

    def _dump(self, template):
        super()._dump(template)
        set_throughput(template, self)


class DynamoDBTable(BaseResource):
    TEMPLATE = \
'''
Type: AWS::DynamoDB::Table
Properties:
  AttributeDefinitions: []
  KeySchema: []
  ProvisionedThroughput: {}
  StreamSpecification: {}
  LocalSecondaryIndexes: []
  GlobalSecondaryIndexes: []
  Tags: []
DependsOn: []
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][name + 'Arn'] = make_output(Custom('!GetAtt', name + '.Arn'))
        set_depends_on(template, self)

    def _dump_properties(self, properties):
        properties['TableName'] = self.get('table_name')
        for obj in self.get('attribute_definitions', []):
            name, value = take_pair(obj)
            properties['AttributeDefinitions'].append({
                'AttributeName': name,
                'AttributeType': value
            })
        set_key_schema(properties, self)
        set_throughput(properties, self)
        try_set_field(properties['StreamSpecification'], 'StreamViewType',
            self.get_path('stream_specification.stream_view_type'))
        set_sub_list(properties['LocalSecondaryIndexes'],
            self, 'local_secondary_indexes', LocalSecondaryIndex)
        set_sub_list(properties['GlobalSecondaryIndexes'],
            self, 'global_secondary_indexes', GlobalSecondaryIndex)
        set_tags_list(properties, self)


Root.RESOURCE_TYPES['dynamodb-table'] = DynamoDBTable


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
    return Root(source)

pattern = create_pattern()
