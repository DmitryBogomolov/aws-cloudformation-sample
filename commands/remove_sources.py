import operator
from utils import helper
from utils.client import client
from utils.template import template
from utils.logger import log

s3_client = client('s3')

def run():
    log('Removing sources')
    objects = []
    bucket = template['Bucket']
    res = s3_client.list_objects(Bucket=bucket, Prefix=template['Project'] + '/')
    keys = list(map(operator.itemgetter('Key'), res['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3_client.delete_objects(Bucket=template['Bucket'], Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
