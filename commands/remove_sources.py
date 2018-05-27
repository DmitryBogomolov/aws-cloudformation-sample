import boto3
import operator
import helper
from utils.logger import log

s3_client = boto3.client('s3')

def run():
    log('Removing sources')
    template = helper.load_template()
    objects = []
    bucket = template['Bucket']
    res = s3_client.list_objects(Bucket=bucket, Prefix=template['Project'] + '/')
    keys = list(map(operator.itemgetter('Key'), res['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3_client.delete_objects(Bucket=template['Bucket'], Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
