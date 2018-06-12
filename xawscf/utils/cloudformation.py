from botocore.exceptions import WaiterError
from .client import client
from ..pattern.const import SOURCES_BUCKET

cf = client('cloudformation')

def wait(name, stack_name, delay, **kwargs):
    waiter = cf.get_waiter(name)
    waiter.wait(
        StackName=stack_name,
        WaiterConfig={ 'Delay': delay },
        **kwargs
    )

def get_stack_info(stack_name):
    response = cf.describe_stacks(StackName=stack_name)
    return response['Stacks'][0]

def get_sources_bucket(stack_name):
    stack = get_stack_info(stack_name)
    return next(output['OutputValue']
        for output in stack['Outputs'] if output['OutputKey'] == SOURCES_BUCKET)
