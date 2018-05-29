from utils import helper
from utils.pattern import pattern
from utils.logger import log
from utils.yaml import save

def create_template(pattern):
    template = {}
    template['AWSTemplateFormatVersion'] = '2010-09-09'
    template['Transform'] = 'AWS::Serverless-2016-10-31'
    template['Description'] = pattern.description
    template['Resources'] = dict(pattern.Resources)
    return template

def create_functions(template, pattern):
    s3_base_path = 's3://{0}/{1}/'.format(pattern.bucket, pattern.project)
    for function in pattern.functions:
        resource = {
            'Type': 'AWS::Serverless::Function',
            'Properties': function.Properties
        }
        s3_path = s3_base_path + helper.get_archive_name(function.code_uri)
        resource['Properties'].update(
            FunctionName=function.full_name,
            Description=function.description,
            Runtime=function.runtime,
            Timeout=function.timeout,
            Tags=function.tags,
            Handler=function.handler,
            CodeUri=s3_path
        )
        if function.environment:
            env = resource['Properties'].get('Environment')
            if not env:
                env = { 'Variables': {} }
                resource['Properties']['Environment'] = env
            env['Variables'].update(function.environment)

def save_template(template):
    file_path = helper.get_processed_template_path()
    save(file_path, template);
    log('Saved to {}', file_path)

def run():
    log('Processing {}', helper.get_pattern_path())
    helper.ensure_folder()
    template = create_template(pattern)
    create_functions(template, pattern)
    save_template(template)
