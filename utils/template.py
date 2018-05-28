from . import helper
from .yaml import load

CUSTOM_FIELDS = (
    'Project',
    'Bucket',
    'Profile'
)

template = load(helper.get_template_path())

if not template.get('Profile'):
    template['Profile'] = 'default'

for field in CUSTOM_FIELDS:
    if not field in template:
        raise Exception('"{}" field is absent.'.format(field))
