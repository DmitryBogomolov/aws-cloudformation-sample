from os import getcwd, path
import yaml

# pylint: disable=too-few-public-methods
class Custom(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __eq__(self, other):
        return self.tag == other.tag and self.value == other.value

def custom_constructor(loader, node):
    construct = getattr(loader, 'construct_' + node.id)
    return Custom(node.tag, construct(node))

TYPE_TO_REPRESENTER = {
    'list': 'sequence',
    'dict': 'mapping'
}

def custom_representer(dumper, data):
    represent = getattr(dumper,
        'represent_' + TYPE_TO_REPRESENTER.get(type(data.value).__name__, 'scalar'))
    return represent(data.tag, data.value)

INTRINSIC_FUNCTIONS = (
    '!Base64',
    '!Cidr',
    '!FindInMap',
    '!GetAtt',
    '!GetAZs',
    '!ImportValue',
    '!Join',
    '!Select',
    '!Split',
    '!Sub',
    '!Ref'
)

for intrinsic in INTRINSIC_FUNCTIONS:
    yaml.add_constructor(intrinsic, custom_constructor)
yaml.add_representer(Custom, custom_representer)

CWD = path.join(getcwd(), '')

def include_file_constructor(loader, node):
    value = loader.construct_scalar(node)
    path_to_file = path.realpath(path.join(path.dirname(loader.stream.name), value))
    if path.commonprefix([CWD, path_to_file]) != CWD:
        raise Exception('File path *{}* is not valid'.format(value))
    return load_template_from_file(path_to_file)

yaml.add_constructor('!include', include_file_constructor)

def load_template(template: str):
    return yaml.load(template, Loader=yaml.Loader)

def load_template_from_file(file_path: str):
    with open(file_path, 'r') as file_object:
        return load_template(file_object)

def save_template_to_file(file_path: str, data):
    with open(file_path, 'w') as file_object:
        yaml.dump(data, file_object, default_flow_style=False, Dumper=yaml.Dumper)
