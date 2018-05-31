from utils.client import client
from utils.pattern import pattern
from utils.logger import log

cf = client('cloudformation')

def run():
    ret = cf.describe_stacks(StackName=pattern.project)
    stack = ret['Stacks'][0]
    log('Name: {}', stack['StackName'])
    log('Status: {}', stack['StackStatus'])
    log('Tags: {}', ', '.join(stack['Tags']) or '-')
    log('Description: {}', stack['Description'])
    log('Creation time: {}', stack['CreationTime'])
    log('Last update time: {}', stack['LastUpdatedTime'])
    for obj in stack['Outputs']:
        log('{} = {}', obj['OutputKey'], obj['OutputValue'])
