from os import path
import zipfile
import boto3
import helper
from deploy_sources import deploy_sources as call_deploy_sources

def build_archive(code_uri, archive_name):
    archive_path = helper.get_archive_path(archive_name)
    with zipfile.ZipFile(archive_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(code_uri, arcname=path.basename(code_uri))

def build_packages(template):
    for code_uri in helper.get_code_uri_list(template):
        archive_name = helper.get_archive_name(code_uri)
        build_archive(code_uri, archive_name)

def pack(deploy_sources=False):
    helper.ensure_folder()
    template = helper.load_template()
    build_packages(template)
    if deploy_sources:
        call_deploy_sources()
