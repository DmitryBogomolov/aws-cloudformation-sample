'''
Updates functions code in single command
'''

from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_code import run as call_update_code

def run(pattern, names=None):
    call_process(pattern)
    call_pack(pattern, names)
    call_upload_code(pattern, names)
    call_update_code(pattern, names)
