'''
Deletes zip archives from s3 bucket.
'''

import operator
from ..utils import helper
from ..utils.client import client
from ..utils.pattern import pattern
from ..utils.logger import log

s3_client = client('s3')

def run():
    log('Removing sources')
    objects = []
    bucket = pattern.get('bucket')
    res = s3_client.list_objects(Bucket=bucket, Prefix=pattern.get('project') + '/')
    keys = list(map(operator.itemgetter('Key'), res['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3_client.delete_objects(Bucket=bucket, Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
