'''
Translates pattern file into cloudformation template file.
'''

from ..utils import helper
from ..utils.logger import log
from ..utils.yaml import save
from ..pattern.pattern import get_pattern

def run(pattern_path=None):
    log('Processing')
    pattern = get_pattern(pattern_path)
    helper.ensure_folder()
    template = pattern.dump()
    file_path = helper.get_processed_template_path()
    save(file_path, template)
    log('Saved to {}', file_path)
