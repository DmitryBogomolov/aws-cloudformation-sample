from ..utils.helper import PATTERN_NAME
from ..utils.loader import load_template_from_file
from .root import Root

def get_pattern(pattern_path: str):
    source = load_template_from_file(pattern_path or PATTERN_NAME)
    return Root(source)
