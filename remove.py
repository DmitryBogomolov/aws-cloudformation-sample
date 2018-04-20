import boto3
import helper

cf = boto3.client('cloudformation')

def remove():
    template = helper.load_template()
    cf.delete_stack(StackName=template['Name'])
