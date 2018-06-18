import boto3

exceptions = boto3.exceptions.botocore.exceptions

def get_client(root, name):
    session = boto3.Session(
        profile_name=root.get('profile', None), region_name=root.get('region', None))
    return session.client(name)
