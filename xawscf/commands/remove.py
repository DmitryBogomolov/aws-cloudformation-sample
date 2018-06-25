'''
Removes project in single command
'''

from ..utils.logger import log
from ..commands.unload_code import run as unload_code
from ..commands.delete_stack import run as delete_stack

def run():
    log('Removing')
    unload_code()
    delete_stack()
    log('Removed')
