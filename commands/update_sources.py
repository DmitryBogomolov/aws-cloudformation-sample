from utils import helper
from utils.client import client
from utils.pattern import pattern
from utils.logger import log, logError

lambda_client = client('lambda')

def run():
    project = pattern.get('project')
    bucket = pattern.get('bucket')
    has_error = False
    for function in pattern.functions:
        s3_key = '{}/{}'.format(project, helper.get_archive_name(function.get('code_uri')))
        try:
            lambda_client.update_function_code(
                FunctionName=function.full_name, S3Bucket=bucket, S3Key=s3_key)
        except Exception as err:
            logError(err)
            has_error = True
        log(' - {}', function.name)
    if has_error:
        return 1
