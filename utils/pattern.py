from . import helper
from .yaml import load

def take_dict(source, field):
    return source.get(field) or {}

class Root(object):
    def __init__(self, source):
        self.Resources = take_dict(source, 'Resources')
        self.project = source['project']
        self.bucket = source['bucket']
        self.description = source.get('description')
        self.profile = source.get('profile')
        self.region = source.get('region')
        self.function_timeout = source.get('function_timeout')
        self.function_runtime = source.get('function_runtime')
        self.resources = []
        self.functions = []
        self.roles = []

class Function(object):
    def __init__(self, name, source, root):
        self.root = root
        self.name = name
        self.Properties = take_dict(source, 'Properties')

        self.description = source.get('description')
        self.full_name = helper.get_function_name(root, name)
        self.handler = source['handler']
        self.code_uri = source['code_uri']
        self.tags = take_dict(source, 'tags')
        self.timeout = source.get('timeout') or root.function_timeout
        self.runtime = source.get('runtime') or root.function_runtime
        self.role = source.get('role')
        self.environment = take_dict(source, 'environment')

class Policy(object):
    def __init__(self, name, statement):
        self.name = name
        self.statement = statement

class LambdaRole(object):
    def __init__(self, name, source, root):
        self.root = root
        self.name = name
        self.Properties = take_dict(source, 'Properties')

        self.policies = [Policy(**obj) for obj in source['policies']]

def check_required_fields(source):
    absent = []
    for field in ('project', 'bucket'):
        if not source.get(field):
            absent.append(field)
    if len(absent) > 0:
        raise Exception('The following fields are not defined: {}'.format(', '.join(absent)))

def process_resources(pattern, source):
    for name, resource in source.items():
        if resource['type'] == 'function':
            function = Function(name, resource, pattern)
            pattern.functions.append(function)
            pattern.resources.append(function)
        elif resource['type'] == 'lambda-role':
            role = LambdaRole(name, resource, pattern)
            pattern.roles.append(role)
            pattern.resources.append(role)

def create_pattern():
    source = load(helper.get_pattern_path())
    check_required_fields(source)
    root = Root(source)
    process_resources(root, take_dict(source, 'resources'))
    return root

pattern = create_pattern()
