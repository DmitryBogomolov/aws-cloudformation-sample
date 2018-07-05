# pylint: disable=invalid-name,too-few-public-methods
class colors(object):
    RESET = '\033[0m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    ORANGE = '\033[33m'
    BLUE = '\033[34m'
    RED = '\033[31m'
    LIGHTGREY = '\033[37m'
    DARKGREY = '\033[90m'

def paint(color, text):
    return color + text + colors.RESET
