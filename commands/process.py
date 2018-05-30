from utils import helper
from utils.pattern import pattern
from utils.logger import log
from utils.yaml import save

def run():
    log('Processing {}', helper.get_pattern_path())
    helper.ensure_folder()
    template = pattern.dump()
    file_path = helper.get_processed_template_path()
    save(file_path, template);
    log('Saved to {}', file_path)
