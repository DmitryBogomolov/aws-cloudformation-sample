import os
import yaml
from collections import namedtuple

PACKAGE_PATH = os.path.abspath('.package')
TEMPLATE_NAME = 'template.yaml'

Custom = namedtuple('Custom', ('tag', 'value'))

def custom_constructor(loader, node):
    return Custom(node.tag, node.value)

def custom_representer(dumper, data):
    return dumper.represent_scalar(data.tag, data.value)

for tag in ('!GetAtt', '!Ref'):
    yaml.add_constructor(tag, custom_constructor)
yaml.add_representer(Custom, custom_representer)

def ensure_folder():
    os.makedirs(PACKAGE_PATH, exist_ok=True)

def load_template():
    with open(os.path.abspath(TEMPLATE_NAME), 'r') as f:
        template = yaml.load(f)
    if not template.get('Name'):
        raise RuntimeError('"Name" field is absent.')
    if not template.get('Bucket'):
        raise RuntimeError('"Bucket" field is absent.')
    return template

def get_archive_name(code_uri):
    name = '_'.join(os.path.split(os.path.normpath(os.path.splitext(code_uri)[0])))
    return name + '.zip'

def get_processed_template_path():
    return os.path.join(PACKAGE_PATH, TEMPLATE_NAME)

def get_archive_path(archive_name):
    return os.path.join(PACKAGE_PATH, archive_name)

def is_function_resource(item):
    return item['Type'] == 'AWS::Serverless::Function'

def get_functions(template):
    return list(filter(is_function_resource, template['Resources'].values()))

def get_function_name(template, name):
    return template['Name'] + '-' + name

def get_code_uri_list(template):
    return list(set(resource['Properties']['CodeUri'] for resource in get_functions(template)))

def get_s3_key(template, name):
    return template['Name'] + '/' + name
