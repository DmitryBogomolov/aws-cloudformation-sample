'''
Deletes zip archives from s3 bucket.
'''

from logging import getLogger
from ..utils import helper
from ..utils.client import get_client
from ..utils.cloudformation import get_sources_bucket

logger = getLogger(__name__)

def run(pattern):
    s3 = get_client(pattern, 's3')
    objects = []
    bucket = get_sources_bucket(get_client(pattern, 'cloudformation'), pattern.get('project'))
    response = s3.list_objects(Bucket=bucket)
    keys = list(map(lambda obj: obj['Key'], response['Contents']))
    objects = [{ 'Key': key } for key in keys]
    s3.delete_objects(Bucket=bucket, Delete={ 'Objects': objects })
    for key in keys:
        logger.info(' - {}'.format(key))
