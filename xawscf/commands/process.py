'''
Translates pattern file into cloudformation template file.
'''

from logging import getLogger
from ..utils import helper
from ..utils.loader import save_template_to_file

logger = getLogger(__name__)

def run(pattern):
    helper.ensure_folder()
    template = pattern.dump()
    file_path = helper.get_processed_template_path()
    save_template_to_file(file_path, template)
    logger.info('Saved to {}'.format(file_path))
