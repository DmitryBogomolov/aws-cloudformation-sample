from ..utils.helper import PATTERN_NAME
from ..utils.yaml import load
from .root import Root

def get_pattern(pattern_path):
    source = load(pattern_path or PATTERN_NAME)
    return Root(source)
