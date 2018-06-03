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

def sanitize_resource_name(name):
    return name.title().replace('-', '').replace('_', '')


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

        # The following allows to avoid declaring "DependsOn: []" in every TEMPLATE field.
        depends_on = template.get('DependsOn')
        if not depends_on:
            depends_on = []
            template['DependsOn'] = depends_on
        depends_on.extend(self.get('DependsOn', []))
        depends_on.extend(self.get('depends_on', []))
        self._dump_properties(properties)


    def _dump_properties(self, properties):
        raise Exception('Not implemented')


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
'''

    def __init__(self, *args):
        super().__init__(*args)
        self.full_name = self.root.get('project') + '-' + self.name
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
'''

    def _dump_properties(self, properties):
        properties['RoleName'] = Custom('!Sub',
            self.root.get('project') + '-${AWS::Region}-' + self.name)
        set_sub_list(properties['Policies'], self, 'policies', Policy)


Root.RESOURCE_TYPES['lambda-role'] = LambdaRole


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


class DynamoDBScalableTarget(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApplicationAutoScaling::ScalableTarget
Properties:
  ScalableDimension: dynamodb:table:WriteCapacityUnits
  ServiceNamespace: dynamodb
'''

    def __init__(self, name, source, root, **kwargs):
        super().__init__(name, source, root)
        self._args = kwargs

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        template['DependsOn'].append(self._args['table'])
        template['DependsOn'].append(self._args['role'])

    def _dump_properties(self, properties):
        properties['ScalableDimension'] = self._args['dimension']
        properties['RoleARN'] = Custom('!GetAtt', self._args['role'] + '.Arn')
        properties['ResourceId'] = {
            'Fn::Sub': [
                self._args['resource'],
                { 'table': Custom('!Ref', self._args['table']) }
            ]
        }
        properties['MinCapacity'] = self.get('min')
        properties['MaxCapacity'] = self.get('max')


class DynamoDBScalingPolicy(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApplicationAutoScaling::ScalingPolicy
Properties:
  PolicyType: TargetTrackingScaling
  TargetTrackingScalingPolicyConfiguration:
    TargetValue: 50.0
    ScaleInCooldown: 60
    ScaleOutCooldown: 60
    PredefinedMetricSpecification:
      PredefinedMetricType: DynamoDBWriteCapacityUtilization
'''

    def __init__(self, name, source, root, **kwargs):
        super().__init__(name, source, root)
        self._args = kwargs

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        template['DependsOn'].append(self._args['table'])
        template['DependsOn'].append(self._args['target'])

    def _dump_properties(self, properties):
        properties['PolicyName'] = self._args['policy_name']
        properties['TargetTrackingScalingPolicyConfiguration'][
            'PredefinedMetricSpecification']['PredefinedMetricType'] = self._args['metric_type']
        properties['ScalingTargetId'] = Custom('!Ref', self._args['target'])


class DynamoDBScalingRole(BaseResource):
    TEMPLATE = \
'''
Type: AWS::IAM::Role
Properties:
  AssumeRolePolicyDocument:
    Version: 2012-10-17
    Statement:
      - Effect: Allow
        Principal:
          Service: application-autoscaling.amazonaws.com
        Action: sts:AssumeRole
  Path: /
  Policies:
    - PolicyName: root
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - dynamodb:DescribeTable
              - dynamodb:UpdateTable
          - Effect: Allow
            Action:
              - cloudwatch:PutMetricAlarm
              - cloudwatch:DescribeAlarms
              - cloudwatch:GetMetricStatistics
              - cloudwatch:SetAlarmState
              - cloudwatch:DeleteAlarms
            Resource: '*'
'''

    def __init__(self, name, source, root, **kwargs):
        super().__init__(name, source, root)
        self._args = kwargs

    def _dump_properties(self, properties):
        properties['Policies'][0]['PolicyDocument']['Statement'][0]['Resource'] = Custom(
            '!GetAtt', self._args['table'] + '.Arn')


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
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][name + 'Arn'] = make_output(Custom('!GetAtt', name + '.Arn'))
        self._setup_autoscaling(parent_template)

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

    def _setup_autoscaling_item(self, parent_template, **kwargs):
        name = self.name
        target_name = name + kwargs['target']
        DynamoDBScalableTarget(
            name=target_name,
            source=kwargs['source'],
            root=self.root,
            table=name,
            resource=kwargs['resource'],
            dimension=kwargs['dimension'],
            role=kwargs['role']
        ).dump(parent_template)
        policy_name = name + kwargs['policy']
        DynamoDBScalingPolicy(
            name=policy_name,
            source={},
            root=self.root,
            table=name,
            policy_name=policy_name,
            metric_type=kwargs['metric'],
            target=target_name
        ).dump(parent_template)

    def _setup_autoscaling(self, parent_template):
        name = self.name
        role_name = name + 'ScalingRole'
        count = 0
        read_capacity = self.get_path('autoscaling.read_capacity')
        write_capacity = self.get_path('autoscaling.write_capacity')
        if read_capacity:
            count += 1
            self._setup_autoscaling_item(parent_template,
                target='ReadScalableTarget',
                source=read_capacity,
                resource='table/${table}',
                dimension='dynamodb:table:ReadCapacityUnits',
                role=role_name,
                policy='ReadScalingPolicy',
                metric='DynamoDBReadCapacityUtilization'
            )
        if write_capacity:
            count += 1
            self._setup_autoscaling_item(parent_template,
                target='WriteScalableTarget',
                source=write_capacity,
                resource='table/${table}',
                dimension='dynamodb:table:WriteCapacityUnits',
                role=role_name,
                policy='WriteScalingPolicy',
                metric='DynamoDBWriteCapacityUtilization'
            )
        for obj in self.get('global_secondary_indexes', []):
            wrapper = Base(obj)
            index_name = wrapper.get('index_name')
            safe_index_name = sanitize_resource_name(index_name)
            index_read_capacity = wrapper.get_path('autoscaling.read_capacity')
            index_write_capacity = wrapper.get_path('autoscaling.write_capacity')
            if index_read_capacity:
                count += 1
                self._setup_autoscaling_item(parent_template,
                    target=safe_index_name + 'ReadScalableTarget',
                    source=index_read_capacity,
                    resource='table/${table}/index/' + index_name,
                    dimension='dynamodb:index:ReadCapacityUnits',
                    role=role_name,
                    policy=safe_index_name + 'ReadScalingPolicy',
                    metric='DynamoDBReadCapacityUtilization'
                )
            if index_write_capacity:
                count += 1
                self._setup_autoscaling_item(parent_template,
                    target=safe_index_name + 'WriteScalableTarget',
                    source=index_write_capacity,
                    resource='table/${table}/index/' + index_name,
                    dimension='dynamodb:index:WriteCapacityUnits',
                    role=role_name,
                    policy=safe_index_name + 'WriteScalingPolicy',
                    metric='DynamoDBWriteCapacityUtilization'
                )
        if count > 0:
            DynamoDBScalingRole(
                name=role_name,
                source={},
                root=self.root,
                table=name
            ).dump(parent_template)


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
