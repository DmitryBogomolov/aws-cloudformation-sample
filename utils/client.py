import boto3
from .template import template

session = boto3.Session(profile_name=template['Profile'])
exceptions = boto3.exceptions.botocore.exceptions

def client(name):
    return session.client(name)
