'''
Updates cloudformation stack.
'''

import time
import hashlib
from ..utils import helper
from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import get_stack_info, watch_stack_status, is_stack_stable
from ..pattern.pattern import get_pattern

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

def update_stack(cf, stack_name, change_set_name):
    cf.execute_change_set(StackName=stack_name, ChangeSetName=change_set_name)
    ret = watch_stack_status(cf, stack_name)
    if ret:
        log('stack is not updated')
        raise Exception(ret)
    log('stack is updated')

def run():
    log('Updating stack')
    pattern = get_pattern()
    stack_name = pattern.get('project')
    template_body = get_template_body()
    cf = get_client(pattern, 'cloudformation')
    cf.validate_template(TemplateBody=template_body)
    if not is_stack_stable(cf, stack_name):
        stack = get_stack_info(cf, stack_name)
        raise Exception('Cannot update stack - {}'.format(stack['StackStatus']))
    change_set_name = 'change-set-' + hashlib.sha256(template_body.encode()).hexdigest()[:8]
    if create_change_set(cf, stack_name, change_set_name, template_body):
        return update_stack(cf, stack_name, change_set_name)
