from utils.yaml import Custom
from .utils import make_output
from .base_resource import BaseResource


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


class ApiGatewayMethod(BaseResource):
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



def get_resource(url, resources):
    if url in resources:
        return resources[url]
    index = url.rindex('/')
    part = url[index + 1:]
    parent_url = url[:index]
    parent = get_resource(parent_url, resources)
    name = part
    if name == '{proxy+}':
        name = 'ProxyVar'
    elif name[0] == '{' and name[-1] == '}':
        name = name[1:-1].title() + 'Var'
    else:
        name = name.title()
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
            urls.append(http_method + ' ' + (url or '/'))
            function = endpoint['function']
            functions.add(function)
            method_name = name + 'Method' + resource['name'] + http_method.title()
            methods.append(method_name)
            ApiGatewayMethod(method_name, {
                'function': function,
                'http_method': http_method,
                'resource': build_resource_id(resource['name'], name),
                'rest_api': name,
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
        properties['Name'] = self.get('name')
