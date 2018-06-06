from .root import Root

from .function import Function
from .function_role import FunctionRole
from .bucket import Bucket
from .dynamodb_table import DynamoDBTable
from .apigateway import ApiGateway
from .statemachine import StateMachine

for resource in [Function, FunctionRole, Bucket, DynamoDBTable, ApiGateway, StateMachine]:
    Root.RESOURCE_TYPES[resource.TYPE] = resource
