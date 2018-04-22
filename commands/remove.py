import boto3
import helper
from .remove_sources import run as call_remove_sources

cf = boto3.client('cloudformation')

def run(remove_sources=False):
    template = helper.load_template()
    cf.delete_stack(StackName=template['Name'])
    if remove_sources:
        call_remove_sources()
