import yaml
from utils import helper
from utils.pattern import pattern, Function, LambdaRole
from utils.logger import log
from utils.yaml import save

ROOT_TEMPLATE = '''
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Description: <Description>
Resources: {}
'''

FUNCTION_TEMPLATE = '''
Type: AWS::Serverless::Function
Properties:
  Environment:
    Variables: {}
  Tags: {}
'''

ROLE_TEMPLATE = '''
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

POLICY_TEMPLATE = '''
PolicyName: <PolicyName>
PolicyDocument:
  Version: 2012-10-17
  Statement: []
'''

def create_template(pattern):
    template = yaml.load(ROOT_TEMPLATE)
    template['Description'] = pattern.description
    template['Resources'].update(pattern.Resources)
    return template

def create_function(function):
    resource = yaml.load(FUNCTION_TEMPLATE)
    properties = resource['Properties']
    properties.update(function.Properties)
    properties.update(
        FunctionName=function.full_name,
        Description=function.description,
        Runtime=function.runtime,
        Timeout=function.timeout,
        Tags=function.tags,
        Handler=function.handler,
        Role=function.role,
        CodeUri='s3://{}/{}/{}'.format(
            pattern.bucket, pattern.project, helper.get_archive_name(function.code_uri))
    )
    if function.environment:
        properties['Environment']['Variables'].update(function.environment)
    return resource

def create_role(role):
    resource = yaml.load(ROLE_TEMPLATE)
    properties = resource['Properties']
    properties.update(role.Properties)
    policy_resouces = []
    for policy in role.policies:
        policy_resouce = yaml.load(POLICY_TEMPLATE)
        policy_resouce['PolicyName'] = policy.name
        policy_resouce['PolicyDocument']['Statement'].extend(policy.statement)
        policy_resouces.append(policy_resouce)
    properties['Policies'].extend(policy_resouces)
    return resource

def create_resources(template, resources):
    for resource in resources:
        if isinstance(resource, Function):
            template[resource.name] = create_function(resource)
        if isinstance(resource, LambdaRole):
            template[resource.name] = create_role(resource)

def save_template(template):
    file_path = helper.get_processed_template_path()
    save(file_path, template);
    log('Saved to {}', file_path)

def run():
    log('Processing {}', helper.get_pattern_path())
    helper.ensure_folder()
    template = create_template(pattern)
    create_resources(template['Resources'], pattern.resources)
    save_template(template)
