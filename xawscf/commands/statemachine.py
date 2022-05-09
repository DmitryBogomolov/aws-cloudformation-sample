'''
Starts (and cancels) state machine.
'''

from logging import getLogger
import time
import json
from ..utils.client import get_client

logger = getLogger(__name__)

def get_arn(sts, name):
    return 'arn:aws:states:{}:{}:stateMachine:{}'.format(
        # pylint: disable=protected-access
        sts._client_config.region_name, sts.get_caller_identity()['Account'], name)

def wait(stepfunctions, execution_arn):
    while True:
        response = stepfunctions.describe_execution(executionArn=execution_arn)
        if response['status'] != 'RUNNING':
            break
        time.sleep(1)
    return response

# pylint: disable=redefined-builtin
def run(pattern, name, input=None, cancel=False):
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        logger.info('State machine *{}* is unknown.'.format(name))
        return 1

    stepfunctions = get_client(pattern, 'stepfunctions')
    if cancel:
        response = stepfunctions.list_executions(
            stateMachineArn=get_arn(get_client(pattern, 'sts'), statemachine.full_name),
            statusFilter='RUNNING'
        )
        for obj in response['executions']:
            stepfunctions.stop_execution(executionArn=obj['executionArn'],
                error='ManuallyStopped', cause='Stopped from script')
        logger.info('canceled')
    else:
        kwargs = {'stateMachineArn': get_arn(get_client(pattern, 'sts'), statemachine.full_name)}
        if input:
            kwargs['input'] = input
        response = stepfunctions.start_execution(**kwargs)
        response = wait(stepfunctions, response['executionArn'])
        if response['status'] != 'SUCCEEDED':
            logger.info(response['status'])
            return 1
        output = json.loads(response['output'])
        logger.info(json.dumps(output, indent=2))
    return 0
