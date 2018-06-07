from .role import Role

class FunctionRole(Role):
    TYPE = 'function-role'
    PRINCIPAL_SERVICE = 'lambda.amazonaws.com'
    MANAGED_POLICIES = ['arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole']
