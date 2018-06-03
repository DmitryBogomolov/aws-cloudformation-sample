import json
from utils.client import client
from utils.pattern import pattern
from utils.logger import log, logError

lambda_client = client('lambda')

def run(name, payload=None):
    log('Invoking function')
    function = pattern.get_function(name)
    if not function:
        log('Function *{}* is unknown.', name)
        return 1
    kwargs = { 'FunctionName': function.full_name }
    if payload:
        kwargs['Payload'] = payload
    try:
        response = lambda_client.invoke(**kwargs)
    except lambda_client.exceptions.ResourceNotFoundException:
        log('Function *{}* is not found.', function.full_name)
        return 1
    except Exception as e:
        logError(e)
        return 1
    payload = json.loads(response['Payload'].read().decode('utf-8'))
    if response.get('FunctionError'):
        error_type = payload.get('errorType')
        log((error_type + ': ' if error_type else '') + payload.get('errorMessage'))
        stack_trace = payload.get('stackTrace')
        if stack_trace:
            for file_name, line, func, code in stack_trace:
                log('  {}, {}, in {}', file_name, line, func)
                log('    {}', code)
        return
    log(json.dumps(payload, indent=2))
