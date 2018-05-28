import boto3
from .template import template

def make_session():
    kwargs = {}
    if template.get('Profile'):
        kwargs['profile_name'] = template['Profile']
    if template.get('Region'):
        kwargs['region_name'] = template['Region']
    return boto3.Session(**kwargs)

session = make_session()
exceptions = boto3.exceptions.botocore.exceptions

def client(name):
    return session.client(name)
