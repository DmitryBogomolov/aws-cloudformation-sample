import yaml
from collections import namedtuple

Custom = namedtuple('Custom', ('tag', 'value'))

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

def load(file_path):
    with open(file_path, 'r') as f:
        return yaml.load(f)

def save(file_path, data):
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
