import yaml
from ..utils.yaml import Custom
from ..utils.helper import get_full_name
from .base_resource import BaseResource


class Role(BaseResource):
    TEMPLATE = \
'''
Type: AWS::IAM::Role
Properties:
  AssumeRolePolicyDocument:
    Version: 2012-10-17
    Statement:
      - Effect: Allow
        Principal: {}
        Action: sts:AssumeRole
  Path: /
  Policies:
    - PolicyDocument:
        Version: 2012-10-17
'''

    STATEMENT_TEMPLATE = '[]'

    PRINCIPAL_SERVICE = None
    MANAGED_POLICIES = None

    TYPE = 'role'

    def _dump_properties(self, properties):
        properties['RoleName'] = Custom('!Sub',
            get_full_name('${AWS::Region}-' + self.name, self.root))
        properties['AssumeRolePolicyDocument']['Statement'][0]['Principal']['Service'] = \
            self.get('principal_service', self.PRINCIPAL_SERVICE)
        managed_policies = self.get('managed_policies', self.MANAGED_POLICIES)
        if managed_policies:
            properties['ManagedPolicyArns'] = managed_policies.copy()
        policy = properties['Policies'][0]
        policy['PolicyName'] = self.name + 'Policy'
        statement = yaml.load(self.STATEMENT_TEMPLATE)
        policy['PolicyDocument']['Statement'] = statement
        statement.extend(self.get('statement', []))
