from os import getenv

def handler(event, context):
    return getenv('VALUE')
