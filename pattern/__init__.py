from .root import Root

from .function import Function
from .function_role import FunctionRole
from .bucket import Bucket
from .dynamodb_table import DynamoDBTable
from .apigateway import ApiGateway

for resource in [Function, FunctionRole, Bucket, DynamoDBTable, ApiGateway]:
    Root.RESOURCE_TYPES[resource.TYPE] = resource
