import os
import yaml
import zipfile
import helper
import boto3

def build_archive(code_uri, archive_name, cache):
    if cache.get(archive_name):
        return
    path_to_archive = os.path.join(helper.PACKAGE_PATH, archive_name)
    with zipfile.ZipFile(path_to_archive, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(code_uri, arcname=os.path.basename(code_uri))
    cache[archive_name] = path_to_archive

def build_packages(template):
    cache = {}
    for resource in helper.get_functions(template):
        code_uri = resource['Properties']['CodeUri']
        archive_name = helper.get_archive_name(code_uri)
        build_archive(code_uri, archive_name, cache)
    return cache

def upload_archives(template, cache):
    s3 = boto3.client('s3')
    for archive_name, path_to_archive in cache.items():
        s3.upload_file(path_to_archive, template['Bucket'], template['Name'] + '/' + archive_name)

def pack(skip_upload=False):
    helper.ensure_folder()
    template = helper.load_template()
    cache = build_packages(template)
    if not skip_upload:
        upload_archives(template, cache)
