import re
from datetime import datetime
from collections import namedtuple
import concurrent.futures
import operator
from utils import helper
from utils.client import client
from utils.template import template
from utils.logger import log, logError

logs_client = client('logs')

get_stream_name = operator.itemgetter('logStreamName')

re_stream_name = re.compile(r'^.*\[(.*)\](.*)$')
re_invocation_start = re.compile(r'^START RequestId: (.*)Version: (.*)$')
re_invocation_end = re.compile(r'^END RequestId: (.*)$')
re_invocation_report = re.compile(
    r'^REPORT RequestId: (.*)Duration: (.*)Billed Duration: (.*)Memory Size: (.*)Max Memory Used: (.*)$')

LogEntry = namedtuple('LogEntry', [
    'function_name', 'instance_version', 'instance_id', 'request_id',
    'duration', 'billed_duration', 'memory_size', 'max_memory_used',
    'start', 'end', 'span',
    'items'
])

LogItem = namedtuple('LogItem', ['timestamp', 'message'])

colors = {
    'RESET': '\033[0m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[93m',
    'ORANGE': '\033[33m',
    'BLUE': '\033[34m'
}

HEADER_TEMPLATE = '{GREEN}{{e.instance_id}} {YELLOW}{{e.request_id}} {BLUE}{{t}} {{e.span}}{RESET}'.format(**colors)
FOOTER_TEMPLATE = '{BLUE}{{e.duration}} {ORANGE}{{e.memory_size}}{RESET}'.format(**colors)
ITEM_TEMPLATE = '{BLUE}+{{offset}}{RESET} {{message}}'.format(**colors)

def find_index(start, end, regexp, events):
    for i in range(start, end):
        match = regexp.search(events[i]['message'].strip())
        if match:
            return i, match

def create_log_item(event):
    kwargs = { 'timestamp': event['timestamp'], 'message': event['message'] }
    return LogItem(**kwargs)

def extract_entry(events, basis):
    entry = basis.copy()
    count = len(events)

    start_index, match = find_index(0, count, re_invocation_start, events)
    entry['request_id'] = match.group(1).strip()
    assert match.group(2).strip() == basis['instance_version']

    end_index, match = find_index(start_index + 1, count, re_invocation_end, events)
    assert match.group(1).strip() == entry['request_id']

    report_index, match = find_index(end_index + 1, count, re_invocation_report, events)
    assert match.group(1).strip() == entry['request_id']
    entry['duration'] = match.group(2).strip()
    entry['billed_duration'] = match.group(3).strip()
    entry['memory_size'] = match.group(4).strip()
    entry['max_memory_used'] = match.group(5).strip()

    start = events[start_index]['timestamp']
    end = events[end_index]['timestamp']
    entry['start'] = start
    entry['end'] = end
    entry['span'] = end - start
    entry['items'] = tuple(map(create_log_item, events[start_index + 1:end_index]))
    return LogEntry(**entry), events[report_index + 1:]

def get_stream_events(function_name, group_name, stream_name):
    events = []
    kwargs = { 'logGroupName': group_name, 'logStreamNames': [stream_name] }
    instance_version, instance_id = re_stream_name.search(stream_name).groups()
    while True:
        response = logs_client.filter_log_events(**kwargs)
        events.extend(response['events'])
        nextToken = response.get('nextToken')
        if nextToken:
            kwargs['nextToken'] = nextToken
        else:
            break
    entries = []
    current_events = events[:]
    basis = {
        'function_name': function_name,
        'instance_version': instance_version,
        'instance_id': instance_id
    }
    while len(current_events) > 0:
        try:
            entry, current_events = extract_entry(current_events, basis)
            entries.append(entry)
        except Exception as e:
            logError(e)
    return stream_name, entries

def load_all_events(function_name, group_name, stream_names):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_stream_events, function_name, group_name, stream_name)
            for stream_name in stream_names]
    done_futures, _ = concurrent.futures.wait(futures)
    events_by_stream = {}
    for future in done_futures:
        stream_name, events = future.result()
        events_by_stream[stream_name] = events
    total_events = []
    for stream_name in stream_names:
        total_events.extend(events_by_stream[stream_name])
    return total_events

def print_event(event):
    timestamp = datetime.fromtimestamp(event.start / 1E3).replace(microsecond=0).isoformat()
    log(HEADER_TEMPLATE.format(e=event, t=timestamp))
    for item in event.items:
        log(ITEM_TEMPLATE.format(offset=item.timestamp - event.start, message=item.message.strip()))
    log(FOOTER_TEMPLATE.format(e=event))
    log('')

def run(name):
    log('Getting logs')
    group_name = '/aws/lambda/' + helper.get_function_name(template, name)
    try:
        streams = logs_client.describe_log_streams(logGroupName=group_name)['logStreams']
    except logs_client.exceptions.ResourceNotFoundException:
        log('Log group *{}* is not found.', group_name)
        return 1
    stream_names = list(map(get_stream_name, streams))
    events = load_all_events(name, group_name, stream_names)
    for event in events:
        print_event(event)
