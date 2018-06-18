from botocore.exceptions import WaiterError
from .const import SOURCES_BUCKET

def wait(cf, name, stack_name, delay, **kwargs):
    waiter = cf.get_waiter(name)
    waiter.wait(StackName=stack_name, WaiterConfig={ 'Delay': delay }, **kwargs)

def get_stack_info(cf, stack_name):
    response = cf.describe_stacks(StackName=stack_name)
    return response['Stacks'][0]

def get_sources_bucket(cf, stack_name):
    outputs = get_stack_info(cf, stack_name)['Outputs']
    return next(filter(lambda obj: obj['OutputKey'] == SOURCES_BUCKET, outputs))['OutputValue']
