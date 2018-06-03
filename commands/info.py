from utils.client import client
from utils.pattern import pattern
from utils.logger import log

cf = client('cloudformation')

def run():
    ret = cf.describe_stacks(StackName=pattern.get('project'))
    stack = ret['Stacks'][0]
    log('Name: {}', stack['StackName'])
    log('Status: {}', stack['StackStatus'])
    log('Tags: {}', ', '.join(stack['Tags']) or '-')
    log('Description: {}', stack['Description'])
    log('Creation time: {}', stack['CreationTime'])
    log('Last update time: {}', stack['LastUpdatedTime'])
    log('')
    for obj in sorted(list(stack['Outputs']), key=lambda obj: obj['OutputKey']):
        log('{:32} {}', obj['OutputKey'], obj['OutputValue'])
    log('')
