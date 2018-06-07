from .root import Root

from .function import Function
from .function_role import FunctionRole
from .role import Role
from .bucket import Bucket
from .dynamodb_table import DynamoDBTable
from .apigateway import ApiGateway
from .statemachine import StateMachine

resources = [
    Function,
    FunctionRole,
    Role,
    Bucket,
    DynamoDBTable,
    ApiGateway,
    StateMachine
]

for resource in resources:
    Root.RESOURCE_TYPES[resource.TYPE] = resource
