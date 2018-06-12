'''
Updates cloudformation stack.
'''

import hashlib
from ..utils import helper
from ..utils.client import client
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log
from ..pattern.pattern import pattern

cf = client('cloudformation')

def get_template_body():
    with open(helper.get_processed_template_path()) as f:
        return f.read()

def update_stack(stack_name, template_body):
    log('creating change set')
    change_set_name = 'change-set-' + hashlib.sha256(template_body.encode()).hexdigest()[:8]
    cf.create_change_set(
        StackName=stack_name,
        Capabilities=('CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'),
        TemplateBody=template_body,
        ChangeSetName=change_set_name
    )
    try:
        wait('change_set_create_complete', stack_name, 5, ChangeSetName=change_set_name)
    except WaiterError as err:
        if err.last_response['StatusReason'] == 'No updates are to be performed.':
            log('no changes')
            return
        raise RuntimeError(err.last_response)
    log('change set is created')
    log('updating stack')
    cf.execute_change_set(
        StackName=stack_name,
        ChangeSetName=change_set_name
    )
    try:
        wait('stack_update_complete', stack_name, 15)
        log('stack is updated')
    except WaiterError as err:
        log('stack is not updated')
        raise RuntimeError(err.last_response)

def run():
    log('Updating stack')
    stack_name = pattern.get('project')
    template_body = get_template_body()
    cf.validate_template(TemplateBody=template_body)
    update_stack(stack_name, template_body)
