import boto3
import helper

lambda_client = boto3.client('lambda')

def find_function_name(template, name):
    resources = helper.get_functions(template)
    for resource in resources:
        if resource['Properties']['FunctionName'] == name:
            return helper.get_function_name(template, name)
    raise RuntimeError('Function *{0}* is not found.'.format(name))

def call_lambda(full_name, payload):
    kwargs = { 'FunctionName': full_name }
    if payload:
        kwargs['Payload'] = payload
    res = lambda_client.invoke(**kwargs)
    payload = res['Payload'].read().decode('utf-8')
    if res.get('FunctionError'):
        raise RuntimeError(payload)
    return payload

def invoke(name, payload=None):
    template = helper.load_template()
    full_name = find_function_name(template, name)
    data = call_lambda(full_name, payload)
    return data
