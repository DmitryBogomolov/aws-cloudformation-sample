from logging import getLogger
import sys
from os import listdir, path
import importlib
import inspect
from ..pattern.pattern import get_pattern

# pylint: disable=too-few-public-methods
class Parameter(object):
    def __init__(self, name):
        self.name = name


# pylint: disable=too-few-public-methods
class Command(object):
    def __init__(self, name, execute, description, parameters):
        self.name = name
        self.execute = execute
        self.description = description
        self.parameters = parameters


logger = getLogger(__name__)

def is_run(arg):
    return arg == 'run'

def is_entry_function(obj):
    return inspect.isfunction(obj) and is_run(obj.__name__)

def make_command(name, func):
    signature = inspect.signature(func) # pylint: disable=no-member
    pattern_parameter = Parameter('pattern')
    setattr(pattern_parameter, 'default', None)
    parameters = [pattern_parameter]
    for parameter in signature.parameters.values():
        if parameter.name == 'pattern':
            continue
        param = Parameter(parameter.name)
        if not parameter.default is signature.empty:
            setattr(param, 'default', parameter.default)
        parameters.append(param)

    name = func.__module__.split('.')[-1]

    def execute(**kwargs):
        logger.info('* {} *'.format(name))
        try:
            pattern = get_pattern(kwargs.get('pattern'))
        except FileNotFoundError as err:
            logger.error('File *{}* does not exist.'.format(err.filename))
            return 1
        kwargs = kwargs.copy()
        kwargs['pattern'] = pattern
        return func(**kwargs)

    return Command(name, execute, sys.modules[func.__module__].__doc__, parameters)

def collect_commands():
    items = []
    for filename in sorted(listdir(path.dirname(__file__))):
        command, ext = path.splitext(filename)
        if ext != '.py' or command == '__init__':
            continue
        mod = importlib.import_module('.' + command, __name__)
        members = inspect.getmembers(mod, is_entry_function)
        if not members:
            continue
        func = next(member for name, member in members if is_run(name))
        items.append(make_command(command, func))
    return items

commands = collect_commands()   # pylint: disable=invalid-name
