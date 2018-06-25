'''
Updates functions code in single command
'''

from ..utils.logger import log
from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_code import run as call_update_code

def run(names=None):
    log('Updating')
    call_process()
    call_pack(names)
    call_upload_code(names)
    call_update_code(names)
    log('Updated')
