'''
Creates cloudformation stack
'''

from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import get_stack_info, watch_stack_status
from ..pattern.root import Root

def run(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    if get_stack_info(cf, stack_name):
        log('stack already exists')
        return 1
    cf.create_stack(StackName=stack_name, TemplateBody=Root.TEMPLATE)
    watch_stack_status(cf, stack_name)
    log('stack is created')
