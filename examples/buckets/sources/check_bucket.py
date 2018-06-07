import os
import boto3

s3 = boto3.client('s3')

def handler(event, context):
    return s3.put_object(
        ACL='public-read',
        Bucket=os.getenv('BUCKET'),
        ContentType='text/plain',
        Key=event['key'],
        Body=event['body'].encode()
    )
