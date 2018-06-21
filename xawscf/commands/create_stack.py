'''
Creates cloudformation stack
'''

from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import watch_stack_status
from ..pattern.root import Root
from ..pattern.pattern import get_pattern

def run():
    log('Creating stack')
    pattern = get_pattern()
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    cf.create_stack(StackName=stack_name, TemplateBody=Root.TEMPLATE)
    log('stack is created')
