'''
Creates cloudformation stack
'''

from ..utils.client import client
from ..utils.logger import log
from ..utils.cloudformation import wait, WaiterError
from ..pattern.root import Root
from ..pattern.pattern import get_pattern

cf = client('cloudformation')

def run():
    log('Creating stack')
    pattern = get_pattern()
    stack_name = pattern.get('project')
    try:
        cf.create_stack(
            StackName=stack_name,
            TemplateBody=Root.TEMPLATE
        )
        log('creating stack')
        wait('stack_create_complete', stack_name, 5)
        log('stack is created')
    except cf.exceptions.AlreadyExistsException:
        log('stack already exists')
    except WaiterError as err:
        log('stack is not created')
        raise RuntimeError(err.last_response)
