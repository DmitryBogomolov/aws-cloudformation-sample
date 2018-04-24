import boto3
import json
import helper

lambda_client = boto3.client('lambda')

def run(name, payload=None):
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
        error_type = payload.get('errorType')
        print((error_type + ': ' if error_type else '') + payload.get('errorMessage'))
        stack_trace = payload.get('stackTrace')
        if stack_trace:
            for file_name, line, func, code in stack_trace:
                print('  {}, {}, in {}'.format(file_name, line, func))
                print('    ' + code)
        return
    print(json.dumps(payload, indent=2))
