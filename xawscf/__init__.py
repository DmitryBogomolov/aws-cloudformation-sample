'''
Executes different commands.
'''

import sys
import argparse
import inspect

from .commands import commands as actions

def setup_subparsers(subparsers):
    for command, func in actions.items():
        signature = inspect.signature(func)
        subparser = subparsers.add_parser(command,
            description=sys.modules[func.__module__].__doc__)
        for parameter in signature.parameters.values():
            args = { 'required': True }
            if parameter.default is not signature.empty:
                args['required'] = False
                if isinstance(parameter.default, bool):
                    args['action'] = 'store_false' if parameter.default else 'store_true'
            subparser.add_argument('--' + parameter.name, **args)

def run():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', description='Select subcommand')
    setup_subparsers(subparsers)

    args = vars(parser.parse_args())
    command = args.pop('command')
    if not command:
        parser.print_help()
        return 0

    return actions[command](**args)
