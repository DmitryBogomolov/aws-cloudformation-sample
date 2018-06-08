'''
Uploads zip archives to s3 bucket.
'''

from boto3.exceptions import S3UploadFailedError
from ..utils import helper
from ..utils.client import client
from ..utils.pattern import pattern
from ..utils.logger import log, logError
from ..utils.parallel import run_parallel

s3_client = client('s3')

def get_s3_key(pattern, name):
    return pattern.get('project') + '/' + name

def deploy_source(code_uri, bucket):
    archive_name = helper.get_archive_name(code_uri)
    key = get_s3_key(pattern, archive_name)
    try:
        s3_client.upload_file(
            helper.get_archive_path(archive_name), bucket, key)
        log(' - {}', key)
    except S3UploadFailedError as err:
        logError(err)

def run(names=None):
    log('Deploying sources')
    bucket = pattern.get('bucket')
    functions = helper.select_functions(pattern, names)
    get_task = lambda code_uri: (deploy_source, [code_uri, bucket])
    run_parallel(map(get_task, helper.get_code_uri_list(functions)))
