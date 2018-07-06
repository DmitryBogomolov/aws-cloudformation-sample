'''
Invokes lambda function.
'''

from logging import getLogger
import json
from ..utils.client import get_client

logger = getLogger(__name__)

def run(pattern, name, payload=None):
    lambda_client = get_client(pattern, 'lambda')
    function = pattern.get_function(name)
    if not function:
        logger.info('Function *{}* is unknown.'.format(name))
        return 1
    kwargs = {'FunctionName': function.full_name}
    if payload:
        kwargs['Payload'] = payload
    try:
        response = lambda_client.invoke(**kwargs)
    except lambda_client.exceptions.ResourceNotFoundException:
        logger.info('Function *{}* is not found.'.format(function.full_name))
        return 1
    except Exception as err:    # pylint: disable=broad-except
        logger.exception(err)
        return 1
    payload = json.loads(response['Payload'].read().decode('utf-8'))
    if response.get('FunctionError'):
        error_type = payload.get('errorType')
        logger.info((error_type + ': ' if error_type else '') + payload.get('errorMessage'))
        stack_trace = payload.get('stackTrace')
        if stack_trace:
            for file_name, line, func, code in stack_trace:
                logger.info('  {}, {}, in {}'.format(file_name, line, func))
                logger.info('    {}'.format(code))
        return 1
    logger.info(json.dumps(payload, indent=2))
