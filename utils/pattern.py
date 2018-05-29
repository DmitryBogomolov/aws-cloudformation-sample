from . import helper
from .yaml import load

def take_dict(source, field):
    return source.get(field) or {}

class Pattern(object):
    pass

class Function(object):
    def __init__(self, name, source, root):
        self.root = root
        self.name = name
        self.description = source.get('description')
        self.full_name = helper.get_function_name(root, name)
        self.handler = source['handler']
        self.code_uri = source['code_uri']
        self.tags = take_dict(source, 'tags')
        self.timeout = source.get('timeout') or root.function_timeout
        self.runtime = source.get('runtime') or root.function_runtime
        self.environment = take_dict(source, 'environment')
        self.Properties = take_dict(source, 'Properties')

def set_basic_fields(pattern, source):
    pattern.project = source['project']
    pattern.bucket = source['bucket']
    pattern.description = source.get('description')
    pattern.profile = source.get('profile')
    pattern.region = source.get('region')
    pattern.function_timeout = source.get('function_timeout')
    pattern.function_runtime = source.get('function_runtime')
    pattern.Resources = source.get('Resources')

def check_required_fields(source):
    absent = []
    for field in ('project', 'bucket'):
        if not source.get(field):
            absent.append(field)
    if len(absent) > 0:
        raise Exception('The following fields are not defined: {}'.format(', '.join(absent)))

def collect_functions(pattern, resources):
    functions = []
    for name, resource in list(resources.items()):
        if resource['type'] == 'function':
            resources.pop(name)
            function = Function(name, resource, pattern)
            functions.append(function)
    pattern.functions = functions

def create_pattern():
    source = load(helper.get_pattern_path())
    pattern = Pattern()
    check_required_fields(source)
    set_basic_fields(pattern, source)
    resources = take_dict(source, 'resources')
    collect_functions(pattern, resources)
    return pattern

pattern = create_pattern()
