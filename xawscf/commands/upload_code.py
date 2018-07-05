'''
Uploads zip archives to s3 bucket.
'''

from logging import getLogger
from boto3.exceptions import S3UploadFailedError
from ..utils import helper
from ..utils.client import get_client
from ..utils.parallel import run_parallel
from ..utils.cloudformation import get_sources_bucket

logger = getLogger(__name__)

def deploy_source(s3, code_uri, bucket):
    archive_name = helper.get_archive_name(code_uri)
    try:
        s3.upload_file(
            helper.get_archive_path(archive_name), bucket, archive_name)
        logger.info(' - {}'.format(archive_name))
    except S3UploadFailedError as err:
        logger.exception(err)

def run(pattern, names=None):
    s3 = get_client(pattern, 's3')
    bucket = get_sources_bucket(get_client(pattern, 'cloudformation'), pattern.get('project'))
    functions = helper.select_functions(pattern, names)
    get_task = lambda code_uri: (deploy_source, [s3, code_uri, bucket])
    run_parallel(map(get_task, helper.get_code_uri_list(functions)))
