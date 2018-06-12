'''
Updates lambda sources.
'''

from ..utils import helper
from ..utils.client import client
from ..utils.pattern import pattern
from ..utils.logger import log, logError
from ..utils.parallel import run_parallel
from ..utils.cloudformation import get_sources_bucket

lambda_client = client('lambda')

def update_source(function, bucket):
    try:
        lambda_client.update_function_code(FunctionName=function.full_name,
            S3Bucket=bucket, S3Key=helper.get_archive_name(function.get('code_uri')))
        log(' - {}', function.name)
    except Exception as err:
        logError(err)

def run(names=None):
    bucket = get_sources_bucket(pattern.get('project'))
    functions = helper.select_functions(pattern, names)
    get_task = lambda function: (update_source, [function, bucket])
    run_parallel(map(get_task, functions))
