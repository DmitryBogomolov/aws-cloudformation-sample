from utils import helper
from utils.client import client
from utils.pattern import pattern
from utils.cf_waiter import wait
from utils.logger import log
from .remove_sources import run as call_remove_sources

cf = client('cloudformation')

def delete_stack(stack_name):
    cf.delete_stack(StackName=stack_name)
    wait('stack_delete_complete', stack_name, 5)

def run(remove_sources=False):
    log('Removing stack')
    delete_stack(pattern.get('project'))
    log('Done')
    if remove_sources:
        call_remove_sources()
