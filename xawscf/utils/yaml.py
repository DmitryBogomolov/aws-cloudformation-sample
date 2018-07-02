from os import getcwd, path
import yaml

class Custom(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

    def __eq__(self, other):
        return self.tag == other.tag and self.value == other.value

def custom_constructor(loader, node):
    construct = getattr(loader, 'construct_' + node.id)
    return Custom(node.tag, construct(node))

type_to_representer = {
    'list': 'sequence',
    'dict': 'mapping'
}

def custom_representer(dumper, data):
    represent = getattr(dumper,
        'represent_' + type_to_representer.get(type(data.value).__name__, 'scalar'))
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

for tag in INTRINSIC_FUNCTIONS:
    yaml.add_constructor(tag, custom_constructor)
yaml.add_representer(Custom, custom_representer)

CWD = path.join(getcwd(), '')

def include_file_constructor(loader, node):
    value = loader.construct_scalar(node)
    path_to_file = path.realpath(path.join(path.dirname(loader.stream.name), value))
    if path.commonprefix([CWD, path_to_file]) != CWD:
        raise Exception('File path *{}* is not valid'.format(value))
    return load(path_to_file)

yaml.add_constructor('!include', include_file_constructor)

def load(file_path):
    with open(file_path, 'r') as f:
        return yaml.load(f)

def save(file_path, data):
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
