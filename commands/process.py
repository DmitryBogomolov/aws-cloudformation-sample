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
    for function in pattern.functions:
        resource = {
            'Type': 'AWS::Serverless::Function',
            'Properties': function.Properties
        }
        resource['Properties'].update(
            FunctionName=function.full_name,
            Description=function.description,
            Runtime=function.runtime,
            Timeout=function.timeout,
            Tags=function.tags,
            Handler=function.handler,
            CodeUri=function.code_uri
        )
        template['Resources'][function.name] = resource

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
