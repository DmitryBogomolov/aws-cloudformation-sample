'''
Uploads zip archives to s3 bucket.
'''

from boto3.exceptions import S3UploadFailedError
from ..utils import helper
from ..utils.client import get_client
from ..utils.logger import log, logError
from ..utils.parallel import run_parallel
from ..pattern.pattern import get_pattern
from ..utils.cloudformation import get_sources_bucket

def deploy_source(s3, code_uri, bucket):
    archive_name = helper.get_archive_name(code_uri)
    try:
        s3.upload_file(
            helper.get_archive_path(archive_name), bucket, archive_name)
        log(' - {}', archive_name)
    except S3UploadFailedError as err:
        logError(err)

def run(names=None):
    log('Deploying sources')
    pattern = get_pattern()
    s3 = get_client(pattern, 's3')
    bucket = get_sources_bucket(get_client(pattern, 'cloudformation'), pattern.get('project'))
    functions = helper.select_functions(pattern, names)
    get_task = lambda code_uri: (deploy_source, [s3, code_uri, bucket])
    run_parallel(map(get_task, helper.get_code_uri_list(functions)))
