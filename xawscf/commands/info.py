'''
Gets cloudformation stack info.
'''

from ..utils.client import client, exceptions
from ..utils.pattern import pattern
from ..utils.logger import log
from ..utils.cloudformation import get_stack_info

cf = client('cloudformation')

FIELDS = (
    ('Name', 'StackName'),
    ('Status', 'StackStatus'),
    ('Tags', 'Tags'),
    ('Description', 'Description'),
    ('Creation time', 'CreationTime'),
    ('Last update time', 'LastUpdatedTime')
)

def run():
    try:
        stack = get_stack_info(pattern.get('project'))
    except exceptions.ClientError as err:
        log(err.response['Error']['Message'])
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
