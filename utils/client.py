import boto3
from .pattern import pattern

def make_session():
    kwargs = {}
    profile = pattern.try_get('profile')
    if profile:
        kwargs['profile_name'] = profile
    region = pattern.try_get('region')
    if region:
        kwargs['region_name'] = region
    return boto3.Session(**kwargs)

session = make_session()
exceptions = boto3.exceptions.botocore.exceptions

def client(name):
    return session.client(name)
