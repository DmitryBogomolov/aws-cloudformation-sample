from .utils import try_set_field
from .base_resource import BaseResource

class ApiGateway(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::RestApi
Properties: {}
'''

    TYPE = 'apigateway'

    def _dump_properties(self, properties):
        properties['Name'] = self.get('name')

#   TestApiGateway1:
#     DependsOn: []
#     Properties:
#       Name: api-gateway-1
#       EndpointConfiguration:
#         Types:
#           - EDGE
#     Type: AWS::ApiGateway::RestApi

#   TestApiGateway1Resource:
#     Type: AWS::ApiGateway::Resource
#     Properties:
#       ParentId: !GetAtt TestApiGateway1.RootResourceId
#       PathPart: '{proxy+}'
#       RestApiId: !Ref TestApiGateway1

#   TestApiGateway1Method1:
#     Type: AWS::ApiGateway::Method
#     Properties:
#       HttpMethod: GET
#       RequestParameters: {}
#       ResourceId: !GetAtt TestApiGateway1.RootResourceId
#       RestApiId: !Ref TestApiGateway1
#       AuthorizationType: NONE
#       Integration:
#         IntegrationHttpMethod: POST
#         Type: AWS_PROXY
#         Uri: !Sub
#           - arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${func}/invocations
#           - { func: !GetAtt ProcessApiRequest.Arn }
#       MethodResponses: []

#   TestApiGateway1Method1Get:
#     Type: AWS::ApiGateway::Method
#     Properties:
#       HttpMethod: GET
#       RequestParameters: {}
#       ResourceId: !Ref TestApiGateway1Resource
#       RestApiId: !Ref TestApiGateway1
#       AuthorizationType: NONE
#       Integration:
#         IntegrationHttpMethod: POST
#         Type: AWS_PROXY
#         Uri: !Sub
#           - arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${func}/invocations
#           - { func: !GetAtt ProcessApiRequest.Arn }
#       MethodResponses: []

#   TestApiGateway1Deployment:
#     Type: AWS::ApiGateway::Deployment
#     Properties:
#       RestApiId: !Ref TestApiGateway1
#       StageName: dev1
#     DependsOn:
#       - TestApiGateway1Method1
#       - TestApiGateway1Method1Get

#   TestApiGateway1Permission:
#     Type: AWS::Lambda::Permission
#     Properties:
#       FunctionName: !GetAtt ProcessApiRequest.Arn
#       Action: lambda:InvokeFunction
#       Principal: !Sub apigateway.${AWS::URLSuffix}
#       SourceArn: !Sub
#         - arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${api}/*/*
#         - { api: !Ref TestApiGateway1 }
