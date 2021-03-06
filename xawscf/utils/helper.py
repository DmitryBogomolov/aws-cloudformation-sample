from os import path, makedirs

PACKAGE_PATH = path.abspath('.package')
PATTERN_NAME = 'pattern.yaml'
TEMPLATE_NAME = 'template.yaml'

def ensure_folder():
    makedirs(PACKAGE_PATH, exist_ok=True)   # pylint: disable=unexpected-keyword-arg

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

def get_full_name(name, root):
    return root.get('project') + '-' + name

def try_set_field(target, name, value):
    if value:
        target[name] = value

def make_output(value):
    return {'Value': value}

def set_tags_list(template, resource):
    items = sorted(resource.get('tags', {}).items(), key=lambda x: x[0])
    tags = ({'Key': key, 'Value': value} for key, value in items)
    template['Tags'].extend(tags)
