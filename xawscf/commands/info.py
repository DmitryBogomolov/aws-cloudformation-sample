'''
Gets cloudformation stack info.
'''

from logging import getLogger
from ..utils.client import get_client
from ..utils.cloudformation import get_stack_info

logger = getLogger(__name__)

FIELDS = (
    ('Name', 'StackName'),
    ('Status', 'StackStatus'),
    ('Tags', 'Tags'),
    ('Description', 'Description'),
    ('Creation time', 'CreationTime'),
    ('Last update time', 'LastUpdatedTime')
)

def run(pattern):
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    stack = get_stack_info(cf, stack_name)
    if not stack:
        logger.info('stack does not exist')
        return 1
    for name, key in FIELDS:
        logger.info('{:20}{}'.format(name, stack.get(key)))
    logger.info('')

    if len(pattern.functions) > 0:
        logger.info('Functions')
        for obj in sorted(pattern.functions, key=lambda obj: obj.name):
            logger.info('  {}'.format(obj.name))
        logger.info('')

    if len(pattern.statemachines) > 0:
        logger.info('State machines')
        for obj in sorted(pattern.statemachines, key=lambda obj: obj.name):
            logger.info('  {}'.format(obj.name))
        logger.info('')

    logger.info('Outputs')
    for obj in sorted(stack['Outputs'], key=lambda obj: obj['OutputKey']):
        logger.info('  {:32}{}'.format(obj['OutputKey'], obj['OutputValue']))
    logger.info('')
