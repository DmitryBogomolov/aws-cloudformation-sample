import yaml
from collections import namedtuple

Custom = namedtuple('Custom', ('tag', 'value'))

def custom_constructor(loader, node):
    return Custom(node.tag, node.value)

def custom_representer(dumper, data):
    return dumper.represent_scalar(data.tag, data.value)

for tag in ('!GetAtt', '!Ref'):
    yaml.add_constructor(tag, custom_constructor)
yaml.add_representer(Custom, custom_representer)

def load(file_path):
    with open(file_path, 'r') as f:
        return yaml.load(f)

def save(file_path, data):
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)