'''
Deletes zip archives from s3 bucket.
'''

import operator
from ..utils import helper
from ..utils.client import client
from ..utils.logger import log
from ..utils.cloudformation import get_sources_bucket
from ..pattern.pattern import pattern

s3_client = client('s3')

def run():
    log('Removing sources')
    objects = []
    bucket = get_sources_bucket(pattern.get('project'))
    response = s3_client.list_objects(Bucket=bucket)
    keys = list(map(operator.itemgetter('Key'), response['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3_client.delete_objects(Bucket=bucket, Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
