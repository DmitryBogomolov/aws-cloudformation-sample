from os import path
from boto3.exceptions import S3UploadFailedError
from utils import helper
from utils.client import client
from utils.template import template
from utils.logger import log, logError

s3_client = client('s3')

def run():
    log('Deploying sources')
    has_error = False
    for code_uri in helper.get_code_uri_list(template):
        archive_name = helper.get_archive_name(code_uri)
        key = helper.get_s3_key(template, archive_name)
        try:
            s3_client.upload_file(
                helper.get_archive_path(archive_name), template['Bucket'], key)
            log(' - {}', key)
        except S3UploadFailedError as err:
            logError(err)
            has_error = True
    return 1 if has_error else 0
