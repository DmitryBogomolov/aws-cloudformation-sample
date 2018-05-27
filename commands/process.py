import helper
from utils.logger import log
from utils.yaml import save

def update_code_uri(template):
    s3_base_path = 's3://{0}/{1}/'.format(template['Bucket'], template['Project'])
    for resource in helper.get_functions(template):
        code_uri = resource['Properties']['CodeUri']
        archive_name = helper.get_archive_name(code_uri)
        resource['Properties']['CodeUri'] = s3_base_path + archive_name

def update_function_names(template):
    for resource in helper.get_functions(template):
        name = resource['Properties']['FunctionName']
        resource['Properties']['FunctionName'] = helper.get_function_name(template, name)

def delete_custom_fields(template):
    template.pop('Project')
    template.pop('Bucket')

def save_template(template):
    file_path = helper.get_processed_template_path()
    save(file_path, template);
    log('Saved to {}', file_path)

def run():
    log('Processing {}', helper.get_template_path())
    helper.ensure_folder()
    template = helper.load_template()
    update_code_uri(template)
    update_function_names(template)
    delete_custom_fields(template)
    save_template(template)
