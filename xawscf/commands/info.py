'''
Gets cloudformation stack info.
'''

from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import get_stack_info
from ..pattern.pattern import get_pattern

FIELDS = (
    ('Name', 'StackName'),
    ('Status', 'StackStatus'),
    ('Tags', 'Tags'),
    ('Description', 'Description'),
    ('Creation time', 'CreationTime'),
    ('Last update time', 'LastUpdatedTime')
)

def run():
    pattern = get_pattern()
    stack_name = pattern.get('project')
    cf = get_client(pattern, 'cloudformation')
    stack = get_stack_info(cf, stack_name)
    if not stack:
        log('stack does not exist')
        return 1
    for name, key in FIELDS:
        log('{:20}{}', name, stack.get(key))
    log('')

    if len(pattern.functions) > 0:
        log('Functions')
        for obj in pattern.functions:
            log('  {}', obj.name)
        log('')

    if len(pattern.statemachines) > 0:
        log('State machines')
        for obj in pattern.statemachines:
            log('  {}', obj.name)
        log('')

    log('Outputs')
    for obj in sorted(stack['Outputs'], key=lambda obj: obj['OutputKey']):
        log('  {:32}{}', obj['OutputKey'], obj['OutputValue'])
    log('')
