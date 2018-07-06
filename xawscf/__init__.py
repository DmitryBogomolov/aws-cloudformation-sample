'''
Executes different commands.
'''

import argparse
import logging
from .commands import commands

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

def setup_subparsers(subparsers):
    for command in commands:
        subparser = subparsers.add_parser(command.name, description=command.description)
        for parameter in command.parameters:
            args = {'required': True}
            if hasattr(parameter, 'default'):
                args['required'] = False
                if isinstance(parameter.default, bool):
                    args['action'] = 'store_false' if parameter.default else 'store_true'
            subparser.add_argument('--' + parameter.name, **args)

def run():
    setup_logger()

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', description='Select subcommand')
    setup_subparsers(subparsers)

    args = vars(parser.parse_args())
    command_name = args.pop('command')
    if not command_name:
        parser.print_help()
        return 0

    execute = next(command.execute for command in commands if command.name == command_name)
    return execute(**args)
