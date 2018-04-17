import boto3
import json
import helper

lambda_client = boto3.client('lambda')

def invoke(name, payload=None):
    template = helper.load_template()
    full_name = helper.get_function_name(template, name)
    kwargs = { 'FunctionName': full_name }
    if payload:
        kwargs['Payload'] = payload
    try:
        response = lambda_client.invoke(**kwargs)
    except lambda_client.exceptions.ResourceNotFoundException:
        print('Function *{}* is not found.'.format(full_name))
        return 1
    except Exception as e:
        print(e)
        return 1
    payload = json.loads(response['Payload'].read().decode('utf-8'))
    if response.get('FunctionError'):
        print(payload['errorType'], payload['errorMessage'])
        stack_trace = payload['stackTrace']
        for file_name, line, func, code in stack_trace:
            print('  {}, {}, in {}'.format(file_name, line, func))
            print('    ' + code)
        return
    print(payload)
