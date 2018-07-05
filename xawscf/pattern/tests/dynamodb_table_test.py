import unittest
from .. import dynamodb_table
from ...utils.loader import Custom

class StubSource(object):
    def __init__(self, data):
        self._data = data

    def get(self, name, default=None):
        return self._data.get(name, default)

    def get_path(self, name):
        obj = self._data
        for item in name.split('.'):
            obj = obj.get(item)
        return obj

class TestDynamoDBTable(unittest.TestCase):
    def test_dump_LocalSecondaryIndex(self):
        obj = dynamodb_table.LocalSecondaryIndex(StubSource({
            'index_name': 'Index1',
            'key_schema': [
                { 'a1': 't1' },
                { 'a2': 't2' }
            ],
            'projection': { 'projection_type': 'projection-type-1' }
        }))

        self.assertEqual(obj.dump(), {
            'IndexName': 'Index1',
            'KeySchema': [
                { 'AttributeName': 'a1', 'KeyType': 't1' },
                { 'AttributeName': 'a2', 'KeyType': 't2' }
            ],
            'Projection': { 'ProjectionType': 'projection-type-1' }
        })

    def test_dump_GlobalSecondaryIndex(self):
        obj = dynamodb_table.GlobalSecondaryIndex(StubSource({
            'index_name': 'Index1',
            'key_schema': [
                { 'a1': 't1' },
                { 'a2': 't2' }
            ],
            'projection': { 'projection_type': 'projection-type-1' },
            'provisioned_throughput': {
                'read_capacity_units': 2,
                'write_capacity_units': 4
            }
        }))

        self.assertEqual(obj.dump(), {
            'IndexName': 'Index1',
            'KeySchema': [
                { 'AttributeName': 'a1', 'KeyType': 't1' },
                { 'AttributeName': 'a2', 'KeyType': 't2' }
            ],
            'Projection': { 'ProjectionType': 'projection-type-1' },
            'ProvisionedThroughput': { 'ReadCapacityUnits': 2, 'WriteCapacityUnits': 4 }
        })

    def test_dump_DynamoDBScalableTarget(self):
        resources = {}
        obj = dynamodb_table.DynamoDBScalableTarget(
            name='Target1', source={ 'min': 1, 'max': 2 }, root=None,
            table='Table1',
            resource='resource-1',
            dimension='dimension-1',
            role='Role1'
        )
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources, {
            'Target1': {
                'Type': 'AWS::ApplicationAutoScaling::ScalableTarget',
                'Properties': {
                    'ScalableDimension': 'dimension-1',
                    'ServiceNamespace': 'dynamodb',
                    'RoleARN': Custom('!GetAtt', 'Role1.Arn'),
                    'ResourceId': Custom('!Sub',
                        ['resource-1', { 'table': Custom('!Ref', 'Table1') }]),
                    'MinCapacity': 1,
                    'MaxCapacity': 2
                },
                'DependsOn': ['Table1', 'Role1']
            }
        })

    def test_dump_DynamoDBScalingPolicy(self):
        self.maxDiff = None
        resources = {}
        obj = dynamodb_table.DynamoDBScalingPolicy(
            name='Policy1', source={}, root=None,
            table='Table1',
            policy_name='policy-1',
            metric_type='metric-1',
            target='Target1'
        )
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources, {
            'Policy1': {
                'Type': 'AWS::ApplicationAutoScaling::ScalingPolicy',
                'Properties': {
                    'PolicyName': 'policy-1',
                    'PolicyType': 'TargetTrackingScaling',
                    'ScalingTargetId': Custom('!Ref', 'Target1'),
                    'TargetTrackingScalingPolicyConfiguration': {
                        'PredefinedMetricSpecification': { 'PredefinedMetricType': 'metric-1' },
                        'ScaleInCooldown': 60,
                        'ScaleOutCooldown': 60,
                        'TargetValue': 50.0
                    }
                },
                'DependsOn': ['Table1', 'Target1']
            }
        })

    def test_dump_DynamoDBScalingRole(self):
        self.maxDiff = None
        resources = {}
        obj = dynamodb_table.DynamoDBScalingRole(
            name='Role1', source={}, root={ 'project': 'project1' },
            table='Table1'
        )
        obj.dump({ 'Resources': resources })

        self.assertEqual(resources['Role1']['Properties']['AssumeRolePolicyDocument']
            ['Statement'][0]['Principal']['Service'], 'application-autoscaling.amazonaws.com')
        self.assertEqual(resources['Role1']['Properties']['Policies'][0]['PolicyDocument']
            ['Statement'], [
                {
                    'Effect': 'Allow',
                    'Action': ['dynamodb:DescribeTable', 'dynamodb:UpdateTable'],
                    'Resource': Custom('!GetAtt', 'Table1.Arn')
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        'cloudwatch:PutMetricAlarm',
                        'cloudwatch:DescribeAlarms',
                        'cloudwatch:GetMetricStatistics',
                        'cloudwatch:SetAlarmState',
                        'cloudwatch:DeleteAlarms'
                    ],
                    'Resource': '*'
                }
            ])

    def test_dump_DynamoDBTable(self):
        self.maxDiff = None
        resources = {}
        outputs = {}
        obj = dynamodb_table.DynamoDBTable('Table1', StubSource({
            'table_name': 'table-1',
            'attribute_definitions': [
                { 'a1': 't1' },
                { 'a2': 't2' }
            ],
            'key_schema': [
                { 'a3': 't3' },
                { 'a4': 't4' }
            ],
            'provisioned_throughput': { 'read_capacity_units': 4, 'write_capacity_units': 4 },
            'stream_specification': { 'stream_view_type': 'stream-view-type-1' },
            'autoscaling': {
                'read_capacity': { 'min': 11, 'max': 21 },
                'write_capacity': { 'min': 12, 'max': 22 }
            }
        }), { 'project': 'project1' })
        obj.dump({ 'Resources': resources, 'Outputs': outputs })

        self.assertEqual(len(resources), 6)

        read_target_properties = resources['Table1ReadScalableTarget']['Properties']
        self.assertEqual(read_target_properties['MinCapacity'], 11)
        self.assertEqual(read_target_properties['MaxCapacity'], 21)
        self.assertEqual(read_target_properties['ResourceId'].value[0], 'table/${table}')

        write_target_properties = resources['Table1WriteScalableTarget']['Properties']
        self.assertEqual(write_target_properties['MinCapacity'], 12)
        self.assertEqual(write_target_properties['MaxCapacity'], 22)
        self.assertEqual(write_target_properties['ResourceId'].value[0], 'table/${table}')

        self.assertEqual(resources['Table1'], {
            'Type': 'AWS::DynamoDB::Table',
            'Properties': {
                'TableName': 'table-1',
                'AttributeDefinitions': [
                    { 'AttributeName': 'a1', 'AttributeType': 't1' },
                    { 'AttributeName': 'a2', 'AttributeType': 't2' }
                ],
                'KeySchema': [
                    { 'AttributeName': 'a3', 'KeyType': 't3' },
                    { 'AttributeName': 'a4', 'KeyType': 't4' }
                ],
                'LocalSecondaryIndexes': [],
                'GlobalSecondaryIndexes': [],
                'ProvisionedThroughput': { 'ReadCapacityUnits': 4, 'WriteCapacityUnits': 4 },
                'StreamSpecification': { 'StreamViewType': 'stream-view-type-1' },
                'Tags': []
            },
            'DependsOn': []
        })

        self.assertEqual(outputs, {
            'Table1': { 'Value': Custom('!Ref', 'Table1') },
            'Table1Arn': { 'Value': Custom('!GetAtt', 'Table1.Arn') }
        })
