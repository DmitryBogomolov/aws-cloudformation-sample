import boto3
from .pattern import pattern

def make_session():
    kwargs = {}
    if pattern.profile:
        kwargs['profile_name'] = pattern.profile
    if pattern.region:
        kwargs['region_name'] = pattern.region
    return boto3.Session(**kwargs)

session = make_session()
exceptions = boto3.exceptions.botocore.exceptions

def client(name):
    return session.client(name)
