from utils import helper
from utils.client import client
from utils.template import template
from utils.logger import log
from .remove_sources import run as call_remove_sources

cf = client('cloudformation')

def delete_stack(stack_name):
    cf.delete_stack(StackName=stack_name)
    waiter = cf.get_waiter('stack_delete_complete')
    waiter.wait(
        StackName=stack_name,
        WaiterConfig={ 'Delay': 5 }
    )

def run(remove_sources=False):
    log('Removing stack')
    delete_stack(template['Project'])
    log('Done')
    if remove_sources:
        call_remove_sources()
