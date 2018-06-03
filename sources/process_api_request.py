import json

def handler(event, context):
    print(event)
    print(context)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'tag': 'Test'
        })
    }
