import boto3
from utils import helper
from utils.client import client, exceptions
from utils.template import template
from utils.logger import log

cf = client('cloudformation')

TEMPLATE_BODY = '''
AWSTemplateFormatVersion: 2010-09-09

Resources:
  StackLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/stack/{project}
'''

def get_template_body():
    with open(helper.get_processed_template_path()) as f:
        return f.read()

def create_stack(stack_name):
    try:
        cf.create_stack(
            StackName=stack_name,
            TemplateBody=TEMPLATE_BODY.format(project=stack_name)
        )
        log('creating stack')
        waiter = cf.get_waiter('stack_create_complete')
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={ 'Delay': 5 }
        )
        log('stack is created')
    except cf.exceptions.AlreadyExistsException:
        log('stack already exists')

def update_stack(stack_name, template_body):
    log('creating change set')
    ret = cf.create_change_set(
        StackName=stack_name,
        Capabilities=('CAPABILITY_IAM',),
        TemplateBody=template_body,
        ChangeSetName='change-set'
    )
    change_id = ret['Id']
    try:
        waiter = cf.get_waiter('change_set_create_complete')
        waiter.wait(
            StackName=stack_name,
            ChangeSetName=change_id,
            WaiterConfig={ 'Delay': 5 }
        )
    except exceptions.WaiterError as err:
        if len(err.last_response['Changes']) == 0:
            log('no changes')
            return
        raise err
    log('change set is created')
    log('updating stack')
    cf.execute_change_set(
        StackName=stack_name,
        ChangeSetName=change_id
    )
    try:
        waiter = cf.get_waiter('stack_update_complete')
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={ 'Delay': 15 }
        )
        log('stack is updated')
    except exceptions.WaiterError as err:
        log('stack is not updated')
        raise RuntimeError(err.last_response)

def run():
    log('Deploying stack')
    stack_name = template['Project']
    template_body = get_template_body()
    cf.validate_template(TemplateBody=template_body)
    create_stack(stack_name)
    update_stack(stack_name, template_body)
    log('Done')
