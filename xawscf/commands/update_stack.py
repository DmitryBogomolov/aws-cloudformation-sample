'''
Updates cloudformation stack.
'''

import time
import hashlib
from datetime import datetime
from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log
from ..pattern.pattern import get_pattern

def get_template_body():
    with open(helper.get_processed_template_path()) as f:
        return f.read()

def create_change_set(cf, stack_name, change_set_name, template_body):
    try:
        cf.create_change_set(
            StackName=stack_name,
            Capabilities=('CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'),
            TemplateBody=template_body,
            ChangeSetName=change_set_name
        )
        wait(cf, 'change_set_create_complete', stack_name, 5, ChangeSetName=change_set_name)
        log('change set is created')
        return True
    except WaiterError as err:
        if err.last_response['StatusReason'] == 'No updates are to be performed.':
            log('no changes')
            return False
        raise RuntimeError(err.last_response)

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
    timestamp = stack.get('LastUpdatedTime', datetime.min)

    while True:
        events = get_stack_events(cf, stack_name, timestamp)
        if len(events) > 0:
            timestamp = events[0]['Timestamp']
            for event in reversed(events):
                log('{:32}{:32}{:32}{}', event['ResourceStatus'], event['ResourceType'],
                    event['LogicalResourceId'], event.get('ResourceStatusReason', ''))
        time.sleep(3)
        status = describe_stack(cf, stack_name)['StackStatus']
        if status.endswith('_COMPLETE'):
            break

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
        update_stack(cf, stack_name, change_set_name)
