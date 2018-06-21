'''
Deletes cloudformation stack.
'''

from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import watch_stack_status
from ..utils.logger import log
from ..pattern.pattern import get_pattern
from .unload_code import run as call_unload_code

def delete_stack(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    cf.delete_stack(StackName=stack_name)

def run(unload_code=False):
    log('Deleting stack')
    pattern = get_pattern()
    delete_stack(pattern)
    log('stack is deleted')
    if unload_code:
        call_unload_code()
