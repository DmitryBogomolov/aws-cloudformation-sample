import sys
from os import listdir, path
import importlib
import inspect
from ..utils.logger import log
from ..pattern.pattern import get_pattern

class Parameter(object):
    def __init__(self, name):
        self.name = name


class Command(object):
    def __init__(self, name, execute, description, parameters):
        self.name = name
        self.execute = execute
        self.description = description
        self.parameters = parameters


def is_run(arg):
    return arg == 'run'

def is_entry_function(obj):
    return inspect.isfunction(obj) and is_run(obj.__name__)

def make_command(name, func):
    signature = inspect.signature(func)
    parameters = []
    for parameter in signature.parameters.values():
        if parameter.name == 'pattern':
            continue
        param = Parameter(parameter.name)
        if not parameter.default is signature.empty:
            param.default = parameter.default
        parameters.append(param)

    name = func.__module__.split('.')[-1]

    def execute(**kwargs):
        log('* {} *'.format(name))
        pattern = get_pattern(kwargs.get('pattern'))
        kwargs = kwargs.copy()
        kwargs['pattern'] = pattern
        return func(**kwargs)

    return Command(name, execute, sys.modules[func.__module__].__doc__, parameters)

commands = []

for filename in sorted(listdir(path.dirname(__file__))):
    command, ext = path.splitext(filename)
    if ext != '.py' or command == '__init__':
        continue
    mod = importlib.import_module('.' + command, __name__)
    members = inspect.getmembers(mod, is_entry_function)
    if len(members) == 0:
        continue
    func = next(member for name, member in members if is_run(name))
    commands.append(make_command(command, func))
