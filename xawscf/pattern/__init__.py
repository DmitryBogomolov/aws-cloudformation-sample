from .root import Root

from .function import Function
from .role import Role
from .bucket import Bucket
from .dynamodb_table import DynamoDBTable
from .apigateway import ApiGateway
from .statemachine import StateMachine

for resource in [
    Function,
    Role,
    Bucket,
    DynamoDBTable,
    ApiGateway,
    StateMachine
]:
    Root.RESOURCE_TYPES[resource.TYPE] = resource
