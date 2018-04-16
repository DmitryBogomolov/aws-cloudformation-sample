#!/usr/bin/env python3

import sys
import argparse
import importlib
import inspect
import functools

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

COMMANDS = ('process', 'pack', 'deploy', 'delete', 'invoke', 'logs')

def is_entry_function(name, obj):
    return inspect.isfunction(obj) and obj.__name__ == name

functions = {}

for command in COMMANDS:
    mod = importlib.import_module(command)
    members = inspect.getmembers(mod, functools.partial(is_entry_function, command))
    if len(members) == 0:
        continue
    func = members[0][1]
    functions[command] = func
    signature = inspect.signature(func)
    subparser = subparsers.add_parser(command)
    for parameter in signature.parameters.values():
        args = { 'required': True }
        if parameter.default is not signature.empty:
            args['required'] = False
        subparser.add_argument('--' + parameter.name, **args)

ret = parser.parse_args()
if not ret.command:
    parser.print_help()
    sys.exit(0)

func = functions[ret.command]
args = vars(ret)
args.pop('command')
res = func(**args)
print(res)
