#!/usr/bin/env python3

import sys
import boto3
import helper

lambda_client = boto3.client('lambda')

def find_function_name(template, name):
    resources = helper.get_functions(template)
    for resource in resources:
        if resource['Properties']['FunctionName'] == name:
            return helper.get_function_name(template, name)
    raise RuntimeError('Function *{0}* is not found.'.format(name))

def invoke(full_name, payload=None):
    kwargs = { 'FunctionName': full_name }
    if payload:
        kwargs['Payload'] = payload
    res = lambda_client.invoke(**kwargs)
    payload = res['Payload'].read().decode('utf-8')
    if res.get('FunctionError'):
        raise RuntimeError(payload)
    return payload

template = helper.load_template()
full_name = find_function_name(template, sys.argv[1])
data = invoke(full_name, sys.argv[2] if len(sys.argv) > 2 else None)
print(data)
