'''
Watches stack update events.
'''

from logging import getLogger
from ..utils.client import get_client
from ..utils.cloudformation import get_stack_info, is_stack_in_progress, watch_stack_status

logger = getLogger(__name__)

def run(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    stack = get_stack_info(cf, stack_name)
    if not stack:
        logger.info('stack does not exist')
        return 1
    if not is_stack_in_progress(stack):
        logger.info('stack is not in progress')
        return 1
    watch_stack_status(cf, logger, stack_name)
    return 0
