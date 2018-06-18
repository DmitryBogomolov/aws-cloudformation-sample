'''
Starts (and cancels) state machine.
'''

import time
import json
from ..utils.client import get_client
from ..utils.logger import log, logError
from ..pattern.pattern import get_pattern

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

def execute_state_machine(name, input):
    log('Starting state machine')
    pattern = get_pattern()
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        log('State machine *{}* is unknown.', name)
        return 1
    kwargs = { 'stateMachineArn': get_arn(get_client(pattern, 'sts'), statemachine.full_name) }
    if input:
        kwargs['input'] = input

    stepfunctions = get_client(pattern, 'stepfunctions')
    response = stepfunctions.start_execution(**kwargs)
    response = wait(stepfunctions, response['executionArn'])
    if response['status'] != 'SUCCEEDED':
        log(response['status'])
        return 1
    output = json.loads(response['output'])
    log(json.dumps(output, indent=2))

def cancel_state_machine(name):
    log('Canceling state machine')
    pattern = get_pattern()
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        log('State machine *{}* is unknown.', name)
        return 1

    stepfunctions = get_client(pattern, 'stepfunctions')
    response = stepfunctions.list_executions(
        stateMachineArn=get_arn(get_client(pattern, 'sts'), statemachine.full_name),
        statusFilter='RUNNING'
    )
    for obj in response['executions']:
        stepfunctions.stop_execution(
            executionArn=obj['executionArn'], error='ManuallyStopped', cause='Stopped from script')
    log('Done')

def run(name, input=None, cancel=False):
    if cancel:
        cancel_state_machine(name)
    else:
        execute_state_machine(name, input)
