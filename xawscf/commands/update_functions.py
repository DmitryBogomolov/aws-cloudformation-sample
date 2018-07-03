'''
Updates functions code in single command
'''

from ..utils.logger import log
from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_code import run as call_update_code

def run(names=None, pattern_path=None):
    log('Updating')
    call_process(pattern_path)
    call_pack(names, pattern_path)
    call_upload_code(names, pattern_path)
    call_update_code(names, pattern_path)
    log('Updated')
