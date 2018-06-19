'''
Deletes cloudformation stack.
'''

from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log
from ..pattern.pattern import get_pattern
from .unload_code import run as call_unload_code

def delete_stack(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    cf.delete_stack(StackName=stack_name)
    try:
        wait(cf, 'stack_delete_complete', stack_name, 5)
    except WaiterError as err:
        raise RuntimeError(err.last_response)

def run(unload_code=False):
    log('Deleting stack')
    pattern = get_pattern()
    delete_stack(pattern)
    log('Done')
    if unload_code:
        call_unload_code()
