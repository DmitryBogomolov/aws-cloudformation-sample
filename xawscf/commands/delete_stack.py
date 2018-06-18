'''
Deletes cloudformation stack.
'''

from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log
from ..pattern.pattern import get_pattern
from .remove_sources import run as call_remove_sources

def delete_stack(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    cf.delete_stack(StackName=stack_name)
    try:
        wait(cf, 'stack_delete_complete', stack_name, 5)
    except WaiterError as err:
        raise RuntimeError(err.last_response)

def run(remove_sources=False):
    log('Deleting stack')
    pattern = get_pattern()
    delete_stack(pattern)
    log('Done')
    if remove_sources:
        call_remove_sources()
