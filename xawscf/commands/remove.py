'''
Removes project in single command
'''

from ..commands.unload_code import run as unload_code
from ..commands.delete_stack import run as delete_stack

def run(pattern):
    unload_code(pattern)
    delete_stack(pattern)
