'''
Uploads zip archives to s3 bucket.
'''

from boto3.exceptions import S3UploadFailedError
from ..utils import helper
from ..utils.client import client
from ..utils.pattern import pattern
from ..utils.logger import log, logError
from ..utils.parallel import run_parallel
from ..utils.cloudformation import get_sources_bucket

s3_client = client('s3')

def deploy_source(code_uri, bucket):
    archive_name = helper.get_archive_name(code_uri)
    try:
        s3_client.upload_file(
            helper.get_archive_path(archive_name), bucket, archive_name)
        log(' - {}', archive_name)
    except S3UploadFailedError as err:
        logError(err)

def run(names=None):
    log('Deploying sources')
    bucket = get_sources_bucket(pattern.get('project'))
    functions = helper.select_functions(pattern, names)
    get_task = lambda code_uri: (deploy_source, [code_uri, bucket])
    run_parallel(map(get_task, helper.get_code_uri_list(functions)))
