import os

def mix(value):
    return (value * 7 + 29) % 17

def handler(event, context):
    return {
        'count': event['count'] - 1,
        'value': mix(event['value'])
    }
