#!/usr/bin/env python3

import sys
import argparse
import importlib

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

COMMANDS = [
    'process',
    'pack',
    'deploy',
    'delete',
    ('invoke', [
        { 'name': 'name', 'required': True },
        'payload'
    ])
]

for command in COMMANDS:
    has_args = isinstance(command, tuple)
    name = command[0] if has_args else command
    subparser = subparsers.add_parser(name)
    if has_args:
        for arg in command[1]:
            kwargs = arg if isinstance(arg, dict) else { 'name': arg }
            dest = '--' + kwargs.pop('name')
            subparser.add_argument(dest, **kwargs)

#process_parser = subparsers.add_parser('process')

#pack_parser = subparsers.add_parser('pack')

#deploy_parser = subparsers.add_parser('deploy')

#delete_parser = subparsers.add_parser('delete')

#invoke_parser = subparsers.add_parser('invoke')
#invoke_parser.add_argument('--name', required=True)
#invoke_parser.add_argument('--payload')

ret = parser.parse_args()
if not ret.command:
    parser.print_help()
    sys.exit(0)

mod = importlib.import_module(ret.command)
func = getattr(mod, ret.command)
args = vars(ret)
args.pop('command')
res = func(**args)
print(res)
