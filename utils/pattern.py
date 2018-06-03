from . import helper
from .yaml import load
from pattern.root import Root

def check_required_fields(source):
    absent = []
    for field in ('project', 'bucket'):
        if not source.get(field):
            absent.append(field)
    if len(absent) > 0:
        raise Exception('The following fields are not defined: {}'.format(', '.join(absent)))

def create_pattern():
    source = load(helper.get_pattern_path())
    check_required_fields(source)
    return Root(source)

pattern = create_pattern()
