'''
Deploys project in single command
'''

from ..utils.logger import log
from ..commands.process import run as call_process
from ..commands.pack import run as call_pack
from ..commands.create_stack import run as call_create_stack
from ..commands.upload_code import run as call_upload_code
from ..commands.update_stack import run as call_update_stack

def run():
    log('Deploying')
    call_process()
    call_pack()
    call_create_stack()
    call_upload_code()
    call_update_stack()
    log('Deployed')
