from utils import helper
from utils.client import client
from utils.pattern import pattern
from utils.logger import log, logError
from utils.parallel import run_parallel

lambda_client = client('lambda')

def update_source(function, project, bucket):
    s3_key = '{}/{}'.format(project, helper.get_archive_name(function.get('code_uri')))
    try:
        lambda_client.update_function_code(
            FunctionName=function.full_name, S3Bucket=bucket, S3Key=s3_key)
        log(' - {}', function.name)
    except Exception as err:
        logError(err)

def run():
    project = pattern.get('project')
    bucket = pattern.get('bucket')
    run_parallel(((update_source, [function, project, bucket])
        for function in pattern.functions))
