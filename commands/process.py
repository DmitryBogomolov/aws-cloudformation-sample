import yaml
import helper

def update_code_uri(template):
    s3_base_path = 's3://{0}/{1}'.format(template['Bucket'], template['Project'])
    for resource in helper.get_functions(template):
        code_uri = resource['Properties']['CodeUri']
        archive_name = helper.get_archive_name(code_uri)
        resource['Properties']['CodeUri'] = s3_base_path + '/' + archive_name

def update_function_names(template):
    for resource in helper.get_functions(template):
        name = resource['Properties']['FunctionName']
        resource['Properties']['FunctionName'] = helper.get_function_name(template, name)

def delete_custom_fields(template):
    template.pop('Project')
    template.pop('Bucket')

def save_template(template):
    with open(helper.get_processed_template_path(), 'w') as f:
        yaml.dump(template, f, default_flow_style=False)

def run():
    helper.ensure_folder()
    template = helper.load_template()
    update_code_uri(template)
    update_function_names(template)
    delete_custom_fields(template)
    save_template(template)
