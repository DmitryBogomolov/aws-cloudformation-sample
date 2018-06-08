import os
import importlib
import inspect
from collections import OrderedDict

commands_dir = os.path.dirname(__file__)

def is_entry_function(obj):
    return inspect.isfunction(obj) and obj.__name__ == 'run'

commands = OrderedDict()

for filename in sorted(os.listdir(commands_dir)):
    command, ext = os.path.splitext(filename)
    if ext != '.py' or command == '__init__':
        continue
    mod = importlib.import_module('.' + command, __name__)
    members = inspect.getmembers(mod, is_entry_function)
    if len(members) == 0:
        continue
    func = next(member for name, member in members if name == 'run')
    commands[command] = func
