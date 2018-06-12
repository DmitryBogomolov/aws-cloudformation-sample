'''
Deletes cloudformation stack.
'''

from ..utils import helper
from ..utils.client import client
from ..utils.pattern import pattern
from ..utils.cloudformation import wait, WaiterError
from ..utils.logger import log
from .remove_sources import run as call_remove_sources

cf = client('cloudformation')

def delete_stack(stack_name):
    cf.delete_stack(StackName=stack_name)
    try:
        wait('stack_delete_complete', stack_name, 5)
    except WaiterError as err:
        raise RuntimeError(err.last_response)

def run(remove_sources=False):
    log('Deleting stack')
    delete_stack(pattern.get('project'))
    log('Done')
    if remove_sources:
        call_remove_sources()
