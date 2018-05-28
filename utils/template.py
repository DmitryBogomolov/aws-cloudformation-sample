from . import helper
from .yaml import load

template = load(helper.get_template_path())

for field in ['Project', 'Bucket']:
    if not field in template:
        raise Exception('"{}" field is absent.'.format(field))
