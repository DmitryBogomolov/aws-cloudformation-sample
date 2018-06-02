import yaml
from . import helper
from .yaml import load, Custom

class Base(object):
    TEMPLATE = None

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

    def get_path(self, name):
        obj = self._source
        for item in name.split('.'):
            obj = obj.get(item)
        return obj

    def dump(self):
        resource = yaml.load(self.TEMPLATE)
        self._dump(resource)
        return resource

    def _dump(self, template):
        raise Exception('Not implemented')


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
        for name, value in self.outputs:
            outputs[name] = { 'Value': value }

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

    def _dump_properties(self, properties):
        raise Exception('Not implemented')


def set_depends_on(template, resource):
    template['DependsOn'].extend(resource.get_list('depends_on'))

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

        output_name = (name, Custom('!Ref', name))
        output_version = (self.version.name, Custom('!Ref', self.version.name))

        return [self.log_group, self.version], [output_name, output_version]

    def _dump(self, template):
        super()._dump(template)
        template['DependsOn'].append(self.log_group.name)
        set_depends_on(template, self)

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

    def _dump(self, template):
        template['PolicyName'] = self.get('name')
        template['PolicyDocument']['Statement'].extend(self.get_list('statement'))


def set_sub_list(target, resource, field, SubResouce):
    target.extend([SubResouce(obj).dump() for obj in resource.get_list(field)])


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

    def init(self):
        return [], []

    def _dump(self, template):
        super()._dump(template)
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
    tags = [{ 'Key': key, 'Value': value } for key, value in resource.get_map('tags').items()]
    template['Tags'].extend(tags)


class S3Bucket(BaseResource):
    TEMPLATE = \
'''
Type: AWS::S3::Bucket
Properties:
  Tags: []
'''

    def init(self):
        name = self.name

        output_name = (name, Custom('!Ref', name))
        output_url = (name + 'Url', Custom('!GetAtt', name + '.WebsiteURL'))

        return [], [output_name, output_url]

    def _dump_properties(self, properties):
        set_tags_list(properties, self)


Root.RESOURCE_TYPES['bucket'] = S3Bucket


def take_pair(obj):
    return list(obj.items())[0]

def set_key_schema(template, resource):
    for obj in resource.get_list('key_schema'):
        name, value = take_pair(obj)
        template['KeySchema'].append({
            'AttributeName': name,
            'KeyType': value
        })

def set_throughput(template, resource):
    source = resource.try_get('provisioned_throughput')
    if source:
        try_set_field(template['ProvisionedThroughput'], 'ReadCapacityUnits',
            source['read_capacity_units'])
        try_set_field(template['ProvisionedThroughput'], 'WriteCapacityUnits',
            source['write_capacity_units'])

class LocalSecondaryIndex(Base):
    TEMPLATE = \
'''
KeySchema: []
Projection: {}
'''

    def _dump(self, template):
        template['IndexName'] = self.get('index_name')
        set_key_schema(template, self)
        projection = self.get_map('projection')
        if projection:
            try_set_field(template['Projection'], 'ProjectionType', projection['projection_type'])


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

    def init(self):
        name = self.name

        output_name = (name, Custom('!Ref', name))
        output_arn = (name + 'Arn', Custom('!GetAtt', name + '.Arn'))

        return [], [output_name, output_arn]

    def _dump(self, template):
        super()._dump(template)
        set_depends_on(template, self)

    def _dump_properties(self, properties):
        properties['TableName'] = self.get('table_name')
        for obj in self.get_list('attribute_definitions'):
            name, value = take_pair(obj)
            properties['AttributeDefinitions'].append({
                'AttributeName': name,
                'AttributeType': value
            })
        set_key_schema(properties, self)
        set_throughput(properties, self)
        stream_specification = self.get_map('stream_specification')
        if stream_specification:
            try_set_field(properties['StreamSpecification'], 'StreamViewType',
                stream_specification['stream_view_type'])
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
    root = Root(source)
    root.init()
    return root

pattern = create_pattern()
