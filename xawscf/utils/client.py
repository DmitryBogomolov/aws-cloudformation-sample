import boto3
from .helper import get_pattern_path
from .yaml import load

def make_session():
    kwargs = {}
    pattern = load(get_pattern_path())
    if 'profile' in pattern:
        kwargs['profile_name'] = pattern['profile']
    if 'region' in pattern:
        kwargs['region_name'] = pattern['region']
    return boto3.Session(**kwargs)

session = make_session()
exceptions = boto3.exceptions.botocore.exceptions

def client(name):
    return session.client(name)
