#!/usr/bin/env python3

import sys
import argparse
import inspect
import xawscf

def setup_subparsers(subparsers):
    for command, func in xawscf.actions.items():
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

def main():
    parser = argparse.ArgumentParser(description=xawscf.__doc__)
    subparsers = parser.add_subparsers(dest='command', description='Select subcommand')
    setup_subparsers(subparsers)

    args = vars(parser.parse_args())
    command = args.pop('command')
    if not command:
        parser.print_help()
        return 0

    return xawscf.actions[command](**args)

if __name__ == '__main__':
    sys.exit(main())
