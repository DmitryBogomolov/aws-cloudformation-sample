from botocore.exceptions import WaiterError
from .client import client

cf = client('cloudformation')

def wait(name, stack_name, delay, **kwargs):
    waiter = cf.get_waiter(name)
    waiter.wait(
        StackName=stack_name,
        WaiterConfig={ 'Delay': delay },
        **kwargs
    )
