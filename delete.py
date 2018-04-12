#!/usr/bin/env python3

import boto3
import helper

cf = boto3.client('cloudformation')

def delete(template):
    cf.delete_stack(StackName=template['Name'])

template = helper.load_template()
delete(template)
