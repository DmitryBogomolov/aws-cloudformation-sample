'''
Translates pattern file into cloudformation template file.
'''

from ..utils import helper
from ..utils.logger import log
from ..utils.yaml import save

def run(pattern):
    helper.ensure_folder()
    template = pattern.dump()
    file_path = helper.get_processed_template_path()
    save(file_path, template)
    log('Saved to {}', file_path)
