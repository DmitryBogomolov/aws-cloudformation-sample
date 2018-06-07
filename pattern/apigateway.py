import yaml
from utils.yaml import Custom
from .utils import get_full_name, make_output
from .base_resource import BaseResource
from .role import Role

class ApiGatewayResouce(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::Resource
Properties: {}
'''

    def _dump_properties(self, properties):
        properties['ParentId'] = self.get('parent')
        properties['PathPart'] = self.get('path_part')
        properties['RestApiId'] = Custom('!Ref', self.get('rest_api'))


class ApiGatewayFunctionMethod(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::Method
Properties:
  RequestParameters: {}
  AuthorizationType: NONE
  Integration:
    IntegrationHttpMethod: POST
    Type: AWS_PROXY
    Uri:
      Fn::Sub:
        - arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${func}/invocations
        - {}
  MethodResponses: []
'''

    def _dump_properties(self, properties):
        properties['HttpMethod'] = self.get('http_method')
        properties['ResourceId'] = self.get('resource')
        properties['RestApiId'] = Custom('!Ref', self.get('rest_api'))
        properties['Integration']['Uri']['Fn::Sub'][1]['func'] = Custom('!GetAtt',
            self.get('function') + '.Arn')


class ApiGatewayPermission(BaseResource):
    TEMPLATE = \
'''
Type: AWS::Lambda::Permission
Properties:
  FunctionName: !GetAtt ProcessApiRequest.Arn
  Action: lambda:InvokeFunction
  Principal: !Sub apigateway.${AWS::URLSuffix}
  SourceArn:
    Fn::Sub:
      - arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${api}/*/*
      - {}
'''

    def _dump_properties(self, properties):
        properties['FunctionName'] = Custom('!GetAtt', self.get('function') + '.Arn')
        properties['SourceArn']['Fn::Sub'][1]['api'] = Custom('!Ref', self.get('rest_api'))


class ApiGatewayS3ObjectRole(Role):
    STATEMENT_TEMPLATE = \
'''
- Effect: Allow
  Action: s3:GetObject
  Resource:
    Fn::Sub:
      - arn:aws:s3:::${bucket}
      - {}
'''

    PRINCIPAL_SERVICE = 'apigateway.amazonaws.com'

    def _dump_properties(self, properties):
        super()._dump_properties(properties)
        statement = properties['Policies'][0]['PolicyDocument']['Statement'][0]
        statement['Resource']['Fn::Sub'][1]['bucket'] = self.get('bucket')


class ApiGatewayBucketMethod(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::Method
Properties:
  RequestParameters:
    method.request.header.Content-Disposition: false
    method.request.header.Content-Type: false
  AuthorizationType: NONE
  HttpMethod: GET
  MethodResponses:
    - StatusCode: 200
      ResponseParameters:
        method.response.header.Timestamp: true
        method.response.header.Content-Length: true
        method.response.header.Content-Type: true
    - StatusCode: 400
    - StatusCode: 500
  Integration:
    IntegrationHttpMethod: GET
    Type: AWS
    Uri:
      Fn::Sub:
        - arn:aws:apigateway:${AWS::Region}:s3:path/${bucket}
        - {}
    PassthroughBehavior: WHEN_NO_MATCH
    RequestParameters:
      integration.request.header.Content-Disposition: method.request.header.Content-Disposition
      integration.request.header.Content-Type: method.request.header.Content-Type
    IntegrationResponses:
      - StatusCode: 200
        ResponseParameters:
          method.response.header.Timestamp: integration.response.header.Date
          method.response.header.Content-Length: integration.response.header.Content-Length
          method.response.header.Content-Type: integration.response.header.Content-Type
      - StatusCode: 400
        SelectionPattern: 4\d{2}
      - StatusCode: 500
        SelectionPattern: 5\d{2}
'''

    def _dump_properties(self, properties):
        properties['ResourceId'] = self.get('resource')
        properties['RestApiId'] = Custom('!Ref', self.get('rest_api'))
        properties['Integration']['Uri']['Fn::Sub'][1]['bucket'] = self.get('bucket')
        properties['Integration']['Credentials'] = Custom('!GetAtt',
            self.get('role_resource') + '.Arn')
        params = filter(None, map(to_param_part, filter(None, self.get('url').split('/'))))
        request_params = properties['RequestParameters']
        integration_request_params = properties['Integration']['RequestParameters']
        for param in params:
            name = 'method.request.path.' + param
            request_params[name] = True
            integration_request_params['integration.request.path.' + param] = name


class ApiGatewayDeployment(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::Deployment
Properties: {}
'''

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        template['DependsOn'].extend(self.get('methods'))

    def _dump_properties(self, properties):
        properties['RestApiId'] = Custom('!Ref', self.get('rest_api'))
        properties['StageName'] = self.get('stage')


def to_param_part(part):
    return part[1:-1] if part[0] == '{' and part[-1] == '}' else ''

def get_resource(url, resources):
    if url in resources:
        return resources[url]
    index = url.rindex('/')
    part = url[index + 1:]
    parent_url = url[:index]
    parent = get_resource(parent_url, resources)
    name = to_param_part(part)
    if name == 'proxy+':
        name = 'ProxyVar'
    elif name:
        name = name.title() + 'Var'
    else:
        name = part.title()
    resource = { 'name': parent['name'] + name, 'part': part, 'parent': parent_url }
    resources[url] = resource
    return resource

def build_resource_name(name, api_name):
    return api_name + 'Resource' + name

def build_resource_id(name, api_name):
    key = '!Ref' if name else '!GetAtt'
    val = build_resource_name(name, api_name) if name else api_name + '.RootResourceId'
    return Custom(key, val)


class ApiGateway(BaseResource):
    TEMPLATE = \
'''
Type: AWS::ApiGateway::RestApi
Properties:
  EndpointConfiguration:
    Types:
      - EDGE
'''

    TYPE = 'apigateway'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        endpoints = self.get('endpoints', [])
        if len(endpoints) == 0:
            return

        name = self.name
        root = self.root
        methods = []
        functions = set()
        resources = {
            '': { 'name': '' }
        }
        urls = []
        for endpoint in endpoints:
            http_method, url = endpoint['path'].split()
            url = url.rstrip('/')
            resource = get_resource(url, resources)
            urls.append('{:4} {}'.format(http_method, url or '/'))
            method_name = name + 'Method' + resource['name'] + http_method.title()
            methods.append(method_name)
            resource_id = build_resource_id(resource['name'], name)
            if 'function' in endpoint:
                function = endpoint['function']
                functions.add(function)
                ApiGatewayFunctionMethod(method_name, {
                    'resource': resource_id,
                    'rest_api': name,
                    'http_method': http_method,
                    'function': function
                }, root).dump(parent_template)
            elif 'bucket' in endpoint:
                # To simplify role actions list - s3:GetObject.
                if http_method != 'GET':
                    raise ValueError('{} - only GET is allowed'.format(url))
                role_name = method_name + 'Role'
                ApiGatewayS3ObjectRole(role_name, {
                    'bucket': endpoint['role_resource']
                }, root).dump(parent_template)
                ApiGatewayBucketMethod(method_name, {
                    'resource': resource_id,
                    'rest_api': name,
                    'role_resource': role_name,
                    'bucket': endpoint['bucket'],
                    'url': url
                }, root).dump(parent_template)
        for obj in resources.values():
            if not obj['name']:
                continue
            ApiGatewayResouce(build_resource_name(obj['name'], name), {
                'parent': build_resource_id(resources[obj['parent']]['name'], name),
                'path_part': obj['part'],
                'rest_api': name
            }, root).dump(parent_template)
        for function in functions:
            ApiGatewayPermission(name + 'Permission' + function, {
                'function': function,
                'rest_api': name
            }, root).dump(parent_template)
        stage = self.get('stage')
        ApiGatewayDeployment(name + 'Deployment', {
            'rest_api': name,
            'stage': stage,
            'methods': methods
        }, root).dump(parent_template)

        outputs = parent_template['Outputs']
        outputs[name + 'Endpoint'] = make_output({
            'Fn::Sub': [
                'https://${gateway}.execute-api.${AWS::Region}.${AWS::URLSuffix}/' + stage,
                { 'gateway': Custom('!Ref', name) }
            ]
        })
        for i, url in enumerate(urls):
            outputs[name + 'Path' + str(i + 1)] = make_output(url)

    def _dump_properties(self, properties):
        properties['Name'] = get_full_name(self.name, self.root)
