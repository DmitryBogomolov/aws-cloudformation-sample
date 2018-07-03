'''
Deploys project in single command
'''

from ..utils.logger import log
from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.create_stack import run as call_create_stack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_stack import run as call_update_stack

def run(pattern_path=None):
    log('Deploying')
    call_process(pattern_path)
    call_pack(pattern_path)
    call_create_stack(pattern_path)
    call_upload_code(pattern_path)
    call_update_stack(pattern_path)
    log('Deployed')
