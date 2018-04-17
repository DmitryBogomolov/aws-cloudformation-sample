import re
from datetime import datetime
import operator
import boto3
import helper

logs_client = boto3.client('logs')

get_stream_name = operator.itemgetter('logStreamName')

def build_name_to_info_map(names):
    result = {}
    regexp = re.compile('.*\[(.*)\](.*)')
    for name in names:
        obj = regexp.search(name)
        result[name] = obj.groups()
    return result

def logs(name):
    template = helper.load_template()
    group = '/aws/lambda/' + helper.get_function_name(template, name)
    try:
        streams = logs_client.describe_log_streams(logGroupName=group)['logStreams']
    except logs_client.exceptions.ResourceNotFoundException:
        print('Log group *{}* is not found.'.format(group))
        return 1
    names = list(map(get_stream_name, streams))
    name_to_info_map = build_name_to_info_map(names)
    paginator = logs_client.get_paginator('filter_log_events')
    iterator = paginator.paginate(logGroupName=group, logStreamNames=names)
    for item in iterator:
        events = item['events']
        for event in events:
            version, instance_id = name_to_info_map[event['logStreamName']]
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1E3)
            message = event['message']
            print('{} {} {}'.format(instance_id, timestamp.replace(microsecond=0).isoformat(), message))
