from utils.yaml import Custom
from .utils import get_full_name, set_sub_list
from .base import Base
from .base_resource import BaseResource

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


class FunctionRole(BaseResource):
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

    TYPE = 'function-role'

    def _dump_properties(self, properties):
        properties['RoleName'] = Custom('!Sub',
            get_full_name('${AWS::Region}-' + self.name, self.root))
        set_sub_list(properties['Policies'], self, 'policies', Policy)
