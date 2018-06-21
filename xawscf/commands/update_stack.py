'''
Updates cloudformation stack.
'''

import time
import hashlib
from datetime import datetime
from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log, logError
from ..utils.text_painter import paint, colors
from ..pattern.pattern import get_pattern

STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': colors.ORANGE,
    'CREATE_COMPLETE': colors.GREEN,
    'CREATE_FAILED': colors.RED,
    'DELETE_IN_PROGRESS': colors.ORANGE,
    'DELETE_COMPLETE': colors.LIGHTGREY,
    'UPDATE_ROLLBACK_COMPLETE': colors.GREEN,
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': colors.RED,
    'UPDATE_ROLLBACK_IN_PROGRESS': colors.RED
}

def get_template_body():
    with open(helper.get_processed_template_path()) as f:
        return f.read()

def create_change_set(cf, stack_name, change_set_name, template_body):
    cf.create_change_set(StackName=stack_name, ChangeSetName=change_set_name,
        TemplateBody=template_body, Capabilities=('CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'))
    response = None
    while True:
        response = cf.describe_change_set(StackName=stack_name, ChangeSetName=change_set_name)
        status = response['Status']
        if status == 'CREATE_COMPLETE' or status == 'FAILED':
            break
        time.sleep(3)
    if status == 'CREATE_COMPLETE' and response['ExecutionStatus'] == 'AVAILABLE':
        log('change set is created')
        return True
    reason = response.get('StatusReason')
    if reason == 'No updates are to be performed.':
        log('no changes')
        return False
    log('change set is not created')
    raise Exception('{} {} {}'.format(status, response['ExecutionStatus'], reason))

def describe_stack(cf, stack_name):
    response = cf.describe_stacks(StackName=stack_name)
    return response['Stacks'][0]

def get_stack_events(cf, stack_name, timestamp):
    events = []
    args = { 'StackName': stack_name }
    is_valid_event = lambda event: event['Timestamp'] > timestamp
    while True:
        response = cf.describe_stack_events(**args)
        batch = list(filter(is_valid_event, response['StackEvents']))
        events.extend(batch)
        token = response.get('NextToken')
        if token and len(batch) > 0:
            args['NextToken'] = token
        else:
            break
    return events

def update_stack(cf, stack_name, change_set_name):
    cf.execute_change_set(StackName=stack_name, ChangeSetName=change_set_name)
    stack = describe_stack(cf, stack_name)
    start_time = stack.get('LastUpdatedTime', stack['CreationTime'])
    event_timestamp = start_time
    align = lambda text: text[:31].ljust(32)
    errors = []

    while True:
        events = get_stack_events(cf, stack_name, event_timestamp)
        if len(events) > 0:
            event_timestamp = events[0]['Timestamp']
            for event in reversed(events):
                status = event['ResourceStatus']
                reason = event.get('ResourceStatusReason', '')
                # TODO: Use `log` here (after it is updated).
                print(str((event['Timestamp'] - start_time).seconds).rjust(3),
                    paint(STATUS_TO_COLOR.get(status, colors.RESET), align(status)),
                    align(event['ResourceType']), align(event['LogicalResourceId']),
                    reason)
                if status.endswith('_FAILED') and reason != 'Resource creation cancelled':
                    errors.append('{} {} {}'.format(
                        event['ResourceType'], event['LogicalResourceId'], reason))
        time.sleep(3)
        if describe_stack(cf, stack_name)['StackStatus'].endswith('_COMPLETE'):
            break

    if len(errors) > 0:
        log('stack is not updated')
        raise Exception(';'.join(errors))
    log('stack is updated')

def run():
    log('Updating stack')
    pattern = get_pattern()
    stack_name = pattern.get('project')
    template_body = get_template_body()
    cf = get_client(pattern, 'cloudformation')
    cf.validate_template(TemplateBody=template_body)
    change_set_name = 'change-set-' + hashlib.sha256(template_body.encode()).hexdigest()[:8]
    if create_change_set(cf, stack_name, change_set_name, template_body):
        return update_stack(cf, stack_name, change_set_name)
