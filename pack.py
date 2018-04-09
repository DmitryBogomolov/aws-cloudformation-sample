#!/usr/bin/env python3

import os
import yaml
import zipfile

DIR_PATH = os.path.abspath('.package')
TEMPLATE_NAME = 'template.yaml'

class Custom(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

def custom_constructor(loader, node):
    return Custom(node.tag, node.value)

def custom_representer(dumper, data):
    return dumper.represent_scalar(data.tag, data.value)

yaml.add_constructor('!GetAtt', custom_constructor)
yaml.add_constructor('!Ref', custom_constructor)
yaml.add_representer(Custom, custom_representer)

code_cache = {}

def build_archive(code_uri, bucket_path):
    path_to_s3 = code_cache.get(code_uri)
    if path_to_s3:
        return path_to_s3
    archive_name = os.path.basename(os.path.splitext(code_uri)[0]) + '.zip'
    path_to_archive = os.path.join(DIR_PATH, archive_name)
    with zipfile.ZipFile(path_to_archive, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(code_uri, arcname=os.path.basename(code_uri))
    path_to_s3 = bucket_path + '/' + archive_name
    code_cache[code_uri] = path_to_s3
    return path_to_s3

def patch_functions_code(template):
    bucket_path = 's3://{0}/{1}'.format(template['Bucket'], template['Name'])
    for key, item in template['Resources'].items():
        if item['Type'] != 'AWS::Serverless::Function':
            continue
        code_uri = item['Properties']['CodeUri']
        path_to_archive = build_archive(code_uri, bucket_path)
        item['Properties']['CodeUri'] = path_to_archive

os.makedirs(DIR_PATH, exist_ok=True)
with open(os.path.abspath(TEMPLATE_NAME), 'r') as f:
    tepmlate = yaml.load(f)

patch_functions_code(tepmlate)

with open(os.path.join(DIR_PATH, TEMPLATE_NAME), 'w') as f:
    yaml.dump(tepmlate, f, default_flow_style=False)
