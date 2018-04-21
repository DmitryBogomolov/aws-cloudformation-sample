import subprocess
import helper

# There is no *boto3.client('cloudformation').deploy* function - have to use *subprocess*.
def invoke_deploy(template):
    args = [
        'aws', 'cloudformation', 'deploy',
        '--stack-name', template['Name'],
        '--capabilities', 'CAPABILITY_IAM',
        '--template-file', helper.get_processed_template_path()
    ]
    with subprocess.Popen(args) as proc:
        proc.communicate()
        if proc.returncode > 0:
            raise RuntimeError('*aws cloudformation deploy* failed ({0})'.format(proc.returncode))

def deploy():
    template = helper.load_template()
    invoke_deploy(template)
