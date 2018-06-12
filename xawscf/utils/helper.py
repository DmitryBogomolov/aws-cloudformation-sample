from os import path, makedirs

PACKAGE_PATH = path.abspath('.package')
PATTERN_NAME = 'pattern.yaml'
TEMPLATE_NAME = 'template.yaml'

def ensure_folder():
    makedirs(PACKAGE_PATH, exist_ok=True)

def get_pattern_path():
    return path.abspath(PATTERN_NAME)

def get_archive_name(code_uri):
    norm = path.relpath(path.normcase(path.normpath(code_uri)))
    if norm.startswith('..'):
        raise RuntimeError('Not valid "CodeUri": {}'.format(code_uri))
    root, ext = path.splitext(norm)
    root = root.replace(path.sep, '_')
    ext = '_' + ext[1:] if ext else ''
    return root + ext + '.zip'

def get_processed_template_path():
    return path.join(PACKAGE_PATH, TEMPLATE_NAME)

def get_archive_path(archive_name):
    return path.join(PACKAGE_PATH, archive_name)

def get_code_uri_list(functions):
    return sorted(set(function.get('code_uri') for function in functions))

def select_functions(pattern, filter_value):
    if filter_value:
        names = set(filter_value.split(','))
        is_valid = lambda function: function.name in names
    else:
        is_valid = lambda _: True
    return filter(is_valid, pattern.functions)
