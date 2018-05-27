import boto3
import helper
from utils.logger import log

s3_client = boto3.client('s3')

def run():
    log('Removing sources')
    template = helper.load_template()
    objects = []
    keys = []
    for code_uri in helper.get_code_uri_list(template):
        archive_name = helper.get_archive_name(code_uri)
        key = helper.get_s3_key(template, archive_name)
        objects.append({ 'Key': key })
        keys.append(key)
    s3_client.delete_objects(Bucket=template['Bucket'], Delete={ 'Objects': objects })
    for key in keys:
        log(' - {}', key)
