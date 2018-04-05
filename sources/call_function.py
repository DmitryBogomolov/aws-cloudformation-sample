import os
import json
import boto3

lambda_client = boto3.client('lambda')

class LambdaError(Exception):
    pass

def handler(event, context):
    # context.function_name
    # context.function_version
    # context.invoked_function_arn
    # context.aws_request_id
    function_name = os.getenv('FUNCTION')
    print('function: {0}'.format(function_name))
    args = { 'FunctionName': function_name }
    payload = os.getenv('PAYLOAD')
    if payload is not None:
        args['Payload'] = payload.encode('utf-8')
    t1 = context.get_remaining_time_in_millis()
    response = lambda_client.invoke(**args)
    t2 = context.get_remaining_time_in_millis()
    print('start: {0}, end: {1}, span: {2}'.format(t1, t2, t1 - t2))
    payload = json.loads(response['Payload'].read().decode('utf-8'))
    print(payload)
    if response.get('FunctionError'):
        raise LambdaError(payload)
    return payload
