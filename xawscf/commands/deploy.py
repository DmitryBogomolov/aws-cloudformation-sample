'''
Deploys project in single command
'''

from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.create_stack import run as call_create_stack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_stack import run as call_update_stack

def run(pattern):
    call_process(pattern)
    call_pack(pattern)
    call_create_stack(pattern)
    call_upload_code(pattern)
    call_update_stack(pattern)
