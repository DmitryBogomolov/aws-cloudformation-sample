'''
Updates lambda sources.
'''

from ..utils import helper
from ..utils.client import get_client
from ..utils.logger import log, logError
from ..utils.parallel import run_parallel
from ..utils.cloudformation import get_sources_bucket
from ..pattern.pattern import get_pattern

def update_source(lambda_client, function, bucket):
    try:
        lambda_client.update_function_code(FunctionName=function.full_name,
            S3Bucket=bucket, S3Key=helper.get_archive_name(function.get('code_uri')))
        log(' - {}', function.name)
    except Exception as err:
        logError(err)

def run(names=None):
    pattern = get_pattern()
    bucket = get_sources_bucket(get_client(pattern, 'cloudformation'), pattern.get('project'))
    functions = helper.select_functions(pattern, names)
    lambda_client = get_client(pattern, 'lambda')
    get_task = lambda function: (update_source, [lambda_client, function, bucket])
    run_parallel(map(get_task, functions))
