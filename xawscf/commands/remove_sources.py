'''
Deletes zip archives from s3 bucket.
'''

import operator
from ..utils import helper
from ..utils.client import get_client
from ..utils.logger import log
from ..utils.cloudformation import get_sources_bucket
from ..pattern.pattern import get_pattern

def run():
    log('Removing sources')
    pattern = get_pattern()
    s3 = get_client(pattern, 's3')
    objects = []
    bucket = get_sources_bucket(get_client(pattern, 'cloudformation'), pattern.get('project'))
    response = s3.list_objects(Bucket=bucket)
    keys = list(map(operator.itemgetter('Key'), response['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3.delete_objects(Bucket=bucket, Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
