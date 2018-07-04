'''
Starts (and cancels) state machine.
'''

import time
import json
from ..utils.client import get_client
from ..utils.logger import log, logError

def get_arn(sts, name):
    return 'arn:aws:states:{}:{}:stateMachine:{}'.format(
        sts._client_config.region_name, sts.get_caller_identity()['Account'], name)

def wait(stepfunctions, execution_arn):
    while True:
        response = stepfunctions.describe_execution(executionArn=execution_arn)
        if response['status'] != 'RUNNING':
            break
        else:
            time.sleep(1)
    return response

def run(pattern, name, input=None, cancel=False):
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        log('State machine *{}* is unknown.', name)
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
        log('canceled')
    else:
        kwargs = { 'stateMachineArn': get_arn(get_client(pattern, 'sts'), statemachine.full_name) }
        if input:
            kwargs['input'] = input
        response = stepfunctions.start_execution(**kwargs)
        response = wait(stepfunctions, response['executionArn'])
        if response['status'] != 'SUCCEEDED':
            log(response['status'])
            return 1
        output = json.loads(response['output'])
        log(json.dumps(output, indent=2))
