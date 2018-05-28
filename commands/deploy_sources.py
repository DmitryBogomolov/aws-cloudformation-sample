from os import path
from utils import helper
from utils.client import client
from utils.template import template
from utils.logger import log

s3_client = client('s3')

def run():
    log('Deploying sources')
    keys = []
    for code_uri in helper.get_code_uri_list(template):
        archive_name = helper.get_archive_name(code_uri)
        key = helper.get_s3_key(template, archive_name)
        keys.append(key)
        s3_client.upload_file(helper.get_archive_path(archive_name), template['Bucket'], key)
        log(' - {}', key)
