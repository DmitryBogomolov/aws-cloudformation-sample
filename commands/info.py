'''
Gets cloudformation stack info.
'''

from utils.client import client, exceptions
from utils.pattern import pattern
from utils.logger import log

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
        response = cf.describe_stacks(StackName=pattern.get('project'))
    except exceptions.ClientError as err:
        log(err.response['Error']['Message'])
        return 1
    stack = response['Stacks'][0]
    for name, key in FIELDS:
        log('{:20}{}', name, stack[key])
    log('')

    log('Functions')
    for obj in pattern.functions:
        log('  {}', obj.name)
    log('')

    log('State machines')
    for obj in pattern.statemachines:
        log('  {}', obj.name)
    log('')

    log('Outputs')
    for obj in sorted(stack['Outputs'], key=lambda obj: obj['OutputKey']):
        log('  {:32}{}', obj['OutputKey'], obj['OutputValue'])
    log('')
