from os import path
import boto3
import helper

s3_client = boto3.client('s3')

def deploy_sources():
    template = helper.load_template()
    keys = []
    for code_uri in helper.get_code_uri_list(template):
        archive_name = helper.get_archive_name(code_uri)
        key = helper.get_s3_key(template, archive_name)
        keys.append(key)
        s3_client.upload_file(helper.get_archive_path(archive_name), template['Bucket'], key)
    for key in keys:
        print('  ', key)
