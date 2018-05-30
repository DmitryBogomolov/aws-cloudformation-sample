import os
from os import path
import zipfile
import shutil
from utils import helper
from utils.pattern import pattern
from utils.logger import log
from .deploy_sources import run as call_deploy_sources

def pack_directory(zf, real_dir, zip_dir):
    for item in os.listdir(real_dir):
        path_to_item = path.join(real_dir, item)
        zip_item = path.join(zip_dir, item)
        if path.isfile(path_to_item):
            zf.write(path_to_item, arcname=zip_item)
        else:
            pack_directory(zf, path_to_item, zip_item)

def build_archive(code_uri):
    archive_name = helper.get_archive_name(code_uri)
    archive_path = helper.get_archive_path(archive_name)
    kind = None
    is_file = path.isfile(code_uri)
    if is_file and path.splitext(code_uri)[1] == '.zip':
        kind = 'zip as-is'
        shutil.copy2(code_uri, archive_path)
    else:
        with zipfile.ZipFile(archive_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            if is_file:
                kind = 'file to zip'
                zf.write(code_uri, arcname=path.basename(code_uri))
            else:
                kind = 'dir to zip'
                pack_directory(zf, code_uri, '')
    log(' - {} -> {} ({})', code_uri, archive_name, kind)

def build_packages(pattern):
    for code_uri in helper.get_code_uri_list(pattern):
        build_archive(code_uri)

def run(deploy_sources=False):
    log('Packing sources')
    helper.ensure_folder()
    build_packages(pattern)
    if deploy_sources:
        call_deploy_sources()
