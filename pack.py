#!/usr/bin/env python3

import os
import yaml
import zipfile
import helper

code_cache = {}

def build_archive(code_uri, archive_name):
    if code_cache.get(archive_name):
        return
    path_to_archive = os.path.join(helper.PACKAGE_PATH, archive_name)
    with zipfile.ZipFile(path_to_archive, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(code_uri, arcname=os.path.basename(code_uri))
    code_cache[code_uri] = True

def build_packages(template):
    for resource in helper.get_functions(template):
        code_uri = resource['Properties']['CodeUri']
        archive_name = helper.get_archive_name(code_uri)
        build_archive(code_uri, archive_name)

helper.ensure_folder()
template = helper.load_template()
build_packages(template)
