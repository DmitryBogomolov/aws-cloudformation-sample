import boto3
from utils import helper
from utils.logger import log
from .remove_sources import run as call_remove_sources

cf = boto3.client('cloudformation')

def run(remove_sources=False):
    log('Removing stack')
    template = helper.load_template()
    cf.delete_stack(StackName=template['Project'])
    if remove_sources:
        call_remove_sources()
