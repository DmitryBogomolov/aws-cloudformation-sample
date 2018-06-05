import os

def handler(event, context):
    return {
        'event': event,
        'result': os.getenv('DATA')
    }
