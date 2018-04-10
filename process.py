#!/usr/bin/env python3

import os
import yaml
import helper

def update_code_uri(template):
    bucket_path = 's3://{0}/{1}'.format(template['Bucket'], template['Name'])
    for resource in helper.get_functions(template):
        code_uri = resource['Properties']['CodeUri']
        archive_name = helper.get_archive_name(code_uri)
        resource['Properties']['CodeUri'] = bucket_path + '/' + archive_name

def update_function_names(template):
    base_name = template['Name']
    for resource in helper.get_functions(template):
        name = resource['Properties']['FunctionName']
        resource['Properties']['FunctionName'] = base_name + '-' + name

def delete_custom_fields(template):
    template.pop('Name')
    template.pop('Bucket')

def save_template(template):
    with open(os.path.join(helper.PACKAGE_PATH, helper.TEMPLATE_NAME), 'w') as f:
        yaml.dump(template, f, default_flow_style=False)

helper.ensure_folder()
template = helper.load_template()
update_code_uri(template)
update_function_names(template)
delete_custom_fields(template)
save_template(template)
