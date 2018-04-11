#!/usr/bin/env python3

import os
import subprocess
import helper

# There is no *boto3.client('cloudformation').deploy* function - have to use *subprocess*.
def deploy(template):
    args = [
        'aws', 'cloudformation', 'deploy',
        '--stack-name', template['Name'],
        '--capabilities', 'CAPABILITY_IAM',
        '--template-file', os.path.join(helper.PACKAGE_PATH, helper.TEMPLATE_NAME)
    ]
    with subprocess.Popen(args) as proc:
        proc.communicate()
        if proc.returncode > 0:
            raise RuntimeError('*aws cloudformation deploy* failed ({0})'.format(proc.returncode))

template = helper.load_template()
deploy(template)
