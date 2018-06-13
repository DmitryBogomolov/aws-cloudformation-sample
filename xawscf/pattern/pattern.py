from ..utils.helper import get_pattern_path
from ..utils.yaml import load
from .root import Root

def get_pattern():
    source = load(get_pattern_path())
    return Root(source)
