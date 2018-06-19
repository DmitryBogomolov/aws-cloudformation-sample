from ..utils.yaml import Custom
from ..utils.helper import try_set_field, make_output, set_tags_list
from .base import Base
from .base_resource import BaseResource
from .role import Role

def take_pair(obj, name_field, value_field):
    ret = {}
    ret[name_field], ret[value_field] = list(obj.items())[0]
    return ret

def set_key_schema(template, resource):
    items = (take_pair(item, 'AttributeName', 'KeyType') for item in resource.get('key_schema'))
    template['KeySchema'].extend(items)

def set_throughput(template, resource):
    template['ProvisionedThroughput']['ReadCapacityUnits'] = \
        resource.get_path('provisioned_throughput.read_capacity_units')
    template['ProvisionedThroughput']['WriteCapacityUnits'] = \
        resource.get_path('provisioned_throughput.write_capacity_units')

class LocalSecondaryIndex(Base):
    TEMPLATE = \
'''
KeySchema: []
Projection: {}
'''

    def _dump(self, template):
        template['IndexName'] = self.get('index_name')
        set_key_schema(template, self)
        template['Projection']['ProjectionType'] = self.get_path('projection.projection_type')


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
  RoleARN: !GetAtt
  ResourceId: !Sub
    - null
    - table: !Ref null
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
        properties['RoleARN'].value = self._args['role'] + '.Arn'
        properties['ResourceId'].value[0] = self._args['resource']
        properties['ResourceId'].value[1]['table'].value = self._args['table']
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
  ScalingTargetId: !Ref null
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
        properties['ScalingTargetId'].value = self._args['target']


class DynamoDBScalingRole(Role):
    STATEMENT_TEMPLATE = \
'''
- Effect: Allow
  Action:
    - dynamodb:DescribeTable
    - dynamodb:UpdateTable
  Resource: !GetAtt null
- Effect: Allow
  Action:
    - cloudwatch:PutMetricAlarm
    - cloudwatch:DescribeAlarms
    - cloudwatch:GetMetricStatistics
    - cloudwatch:SetAlarmState
    - cloudwatch:DeleteAlarms
  Resource: '*'
'''

    PRINCIPAL_SERVICE = 'application-autoscaling.amazonaws.com'

    def __init__(self, name, source, root, **kwargs):
        super().__init__(name, source, root)
        self._args = kwargs

    def _dump_properties(self, properties):
        super()._dump_properties(properties)
        statement = properties['Policies'][0]['PolicyDocument']['Statement'][0]
        statement['Resource'].value = self._args['table'] + '.Arn'


def sanitize_resource_name(name):
    return name.title().replace('-', '').replace('_', '')

def set_indexes(target, resource, field, SubResouce):
    target.extend([SubResouce(obj).dump() for obj in resource.get(field, [])])


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

    TYPE = 'dynamodb-table'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][name + 'Arn'] = make_output(Custom('!GetAtt', name + '.Arn'))
        self._setup_autoscaling(parent_template)

    def _dump_properties(self, properties):
        properties['TableName'] = self.get('table_name')
        properties['AttributeDefinitions'].extend(take_pair(item, 'AttributeName', 'AttributeType')
            for item in self.get('attribute_definitions'))
        set_key_schema(properties, self)
        set_throughput(properties, self)
        try_set_field(properties['StreamSpecification'], 'StreamViewType',
            self.get_path('stream_specification.stream_view_type', None))
        set_indexes(properties['LocalSecondaryIndexes'],
            self, 'local_secondary_indexes', LocalSecondaryIndex)
        set_indexes(properties['GlobalSecondaryIndexes'],
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
