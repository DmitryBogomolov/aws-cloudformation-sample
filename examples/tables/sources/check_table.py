import os
import boto3

dynamodb = boto3.client('dynamodb')

def handler(event, context):
    return dynamodb.put_item(
        TableName=os.getenv('TABLE'),
        Item={
            'id': {
                'S': event['id']
            },
            'timestamp': {
                'N': str(event['timestamp'])
            },
            'type': {
                'S': event['type']
            },
            'position': {
                'N': str(event['position'])
            }
        }
    )
