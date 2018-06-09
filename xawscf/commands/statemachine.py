'''
Starts (and cancels) state machine.
'''

import time
import json
from ..utils.client import session, client
from ..utils.pattern import pattern
from ..utils.logger import log, logError

stepfunctions = client('stepfunctions')
sts = client('sts')

def get_arn(name):
    return 'arn:aws:states:{}:{}:stateMachine:{}'.format(
        session.region_name, sts.get_caller_identity()['Account'], name)

def wait(execution_arn):
    while True:
        response = stepfunctions.describe_execution(executionArn=execution_arn)
        if response['status'] != 'RUNNING':
            break
        else:
            time.sleep(1)
    return response

def execute_state_machine(name, input):
    log('Starting state machine')
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        log('State machine *{}* is unknown.', name)
        return 1
    kwargs = { 'stateMachineArn': get_arn(statemachine.full_name) }
    if input:
        kwargs['input'] = input

    response = stepfunctions.start_execution(**kwargs)
    response = wait(response['executionArn'])
    if response['status'] != 'SUCCEEDED':
        log(response['status'])
        return 1
    output = json.loads(response['output'])
    log(json.dumps(output, indent=2))

def cancel_state_machine(name):
    log('Canceling state machine')
    statemachine = pattern.get_statemachine(name)
    if not statemachine:
        log('State machine *{}* is unknown.', name)
        return 1

    response = stepfunctions.list_executions(
        stateMachineArn=get_arn(statemachine.full_name), statusFilter='RUNNING')
    for obj in response['executions']:
        stepfunctions.stop_execution(
            executionArn=obj['executionArn'], error='ManuallyStopped', cause='Stopped from script')
    log('Done')

def run(name, input=None, cancel=False):
    if cancel:
        cancel_state_machine(name)
    else:
        execute_state_machine(name, input)
