#!/usr/bin/env python3

import sys
import argparse
import importlib
import inspect
import functools

COMMANDS = ('process', 'pack', 'deploy', 'delete', 'invoke', 'logs')

def is_entry_function(name, obj):
    return inspect.isfunction(obj) and obj.__name__ == name

def setup_subparsers(subparsers):
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
    return functions

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    functions = setup_subparsers(subparsers)

    args = vars(parser.parse_args())
    command = args.pop('command')
    if not command:
        parser.print_help()
        return 0

    return functions[command](**args)

if __name__ == '__main__':
    sys.exit(main())
