import subprocess
from utils import helper
from utils.logger import log

# There is no *boto3.client('cloudformation').deploy* function - have to use *subprocess*.
def invoke_deploy(template):
    args = [
        'aws', 'cloudformation', 'deploy',
        '--stack-name', template['Project'],
        '--capabilities', 'CAPABILITY_IAM',
        '--template-file', helper.get_processed_template_path()
    ]
    with subprocess.Popen(args) as proc:
        proc.communicate()

def run():
    log('Deploying stack')
    template = helper.load_template()
    invoke_deploy(template)
