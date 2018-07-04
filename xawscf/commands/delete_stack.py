'''
Deletes cloudformation stack.
'''

from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import get_stack_info, is_stack_in_progress, watch_stack_status
from ..utils.logger import log

def run(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    stack = get_stack_info(cf, stack_name)
    if not stack:
        log('stack does not exist')
        return 1
    if is_stack_in_progress(stack):
        log('stack is in progress')
        return 1
    cf.delete_stack(StackName=stack_name)
    watch_stack_status(cf, stack_name)
    log('stack is deleted')
