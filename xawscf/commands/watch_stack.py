'''
Watches stack update events.
'''

from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import watch_stack_status
from ..pattern.pattern import get_pattern

def run():
    log('Watching stack')
    pattern = get_pattern()
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    watch_stack_status(cf, stack_name)
