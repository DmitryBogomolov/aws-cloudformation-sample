'''
Gets cloudwatch logs for lambda function.
'''

from logging import getLogger, StreamHandler, FileHandler, Formatter, INFO
import re
from datetime import datetime
from collections import namedtuple
from ..utils.client import get_client
from ..utils.parallel import run_parallel
from ..utils.text_painter import colors, paint

logger = getLogger(__name__)
events_logger = getLogger('events')   # pylint: disable=invalid-name
events_logger.setLevel(INFO)

def to_strings(items):
    return map(str, items)

# pylint: disable=no-self-use
class LogEntryFormatter(Formatter):
    def _process_header(self, header):
        return to_strings(header)

    def _process_footer(self, footer):
        return to_strings(footer)

    def _process_item(self, item):
        return to_strings(item)

    def format(self, record):
        header, footer, items = record.msg
        lines = []
        lines.append(' '.join(self._process_header(header)))
        for item in items:
            lines.append(' '.join(self._process_item(item)))
        lines.append(' '.join(self._process_footer(footer)))
        lines.append('')
        return '\n'.join(lines)


def make_colored(color_items, args):
    return (paint(*pair) for pair in zip(color_items, to_strings(args)))

class ColoredLogEntryFormatter(LogEntryFormatter):
    HEADER_COLORS = (colors.GREEN, colors.YELLOW, colors.BLUE, colors.BLUE)
    FOOTER_COLORS = (colors.BLUE, colors.ORANGE)
    ITEM_COLORS = (colors.BLUE, colors.RESET)

    def _process_header(self, header):
        return make_colored(self.HEADER_COLORS, header)

    def _process_footer(self, footer):
        return make_colored(self.FOOTER_COLORS, footer)

    def _process_item(self, item):
        return make_colored(self.ITEM_COLORS, item)


def setup_events_logger(file_name):
    console_handler = StreamHandler()
    console_handler.setFormatter(ColoredLogEntryFormatter())
    events_logger.addHandler(console_handler)

    if file_name:
        file_handler = FileHandler(file_name, mode='w', encoding='utf8')
        file_handler.setFormatter(LogEntryFormatter())
        events_logger.addHandler(file_handler)


RE_STREAM_NAME = re.compile(r'^.*\[(.*)\](.*)$')
RE_INVOCATION_START = re.compile(r'^START RequestId: (.*)Version: (.*)$')
RE_INVOCATION_END = re.compile(r'^END RequestId: (.*)$')
RE_INVOCATION_REPORT = re.compile(
    # pylint: disable=line-too-long
    r'^REPORT RequestId: (.*)Duration: (.*)Billed Duration: (.*)Memory Size: (.*)Max Memory Used: (.*)$')

LogEntry = namedtuple('LogEntry', [
    'function_name', 'instance_version', 'instance_id', 'request_id',
    'duration', 'billed_duration', 'memory_size', 'max_memory_used',
    'start', 'end', 'span',
    'items'
])

LogItem = namedtuple('LogItem', ['timestamp', 'message'])

def find_index(start, end, regexp, events):
    for i in range(start, end):
        match = regexp.search(events[i]['message'].strip())
        if match:
            return i, match
    return None

def create_log_item(event):
    kwargs = {'timestamp': event['timestamp'], 'message': event['message']}
    return LogItem(**kwargs)

def extract_entry(events, basis):
    entry = basis.copy()
    count = len(events)

    start_index, match = find_index(0, count, RE_INVOCATION_START, events)
    entry['request_id'] = match.group(1).strip()
    assert match.group(2).strip() == basis['instance_version']

    end_index, match = find_index(start_index + 1, count, RE_INVOCATION_END, events)
    assert match.group(1).strip() == entry['request_id']

    report_index, match = find_index(end_index + 1, count, RE_INVOCATION_REPORT, events)
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

def get_stream_events(logs, function_name, group_name, stream_name):
    events = []
    kwargs = {'logGroupName': group_name, 'logStreamNames': [stream_name]}
    instance_version, instance_id = RE_STREAM_NAME.search(stream_name).groups()
    while True:
        response = logs.filter_log_events(**kwargs)
        events.extend(response['events'])
        next_token = response.get('nextToken')
        if next_token:
            kwargs['nextToken'] = next_token
        else:
            break
    entries = []
    current_events = events[:]
    basis = {
        'function_name': function_name,
        'instance_version': instance_version,
        'instance_id': instance_id
    }
    while current_events:
        try:
            entry, current_events = extract_entry(current_events, basis)
            entries.append(entry)
        except Exception as err:    # pylint: disable=broad-except
            logger.exception(err)
    return stream_name, entries

def load_all_events(logs, function_name, group_name, stream_names):
    results = run_parallel(((get_stream_events, (logs, function_name, group_name, stream_name))
        for stream_name in stream_names))
    events_by_stream = {}
    for stream_name, events in results:
        events_by_stream[stream_name] = events
    total_events = []
    for stream_name in stream_names:
        total_events.extend(events_by_stream[stream_name])
    return total_events

def print_event(event):
    timestamp = datetime.fromtimestamp(event.start / 1E3).replace(microsecond=0).isoformat()
    header = (event.instance_id, event.request_id, timestamp, event.span)
    footer = (event.duration, event.memory_size)
    items = [(str(item.timestamp - event.start).rjust(4), item.message.strip())
        for item in event.items]
    events_logger.info((header, footer, items))

def run(pattern, name, file_name=None):
    setup_events_logger(file_name)
    logs = get_client(pattern, 'logs')
    function = pattern.get_function(name)
    if not function:
        logger.info('Function *{}* is unknown.'.format(name))
        return 1
    group_name = function.log_group_name
    try:
        streams = logs.describe_log_streams(logGroupName=group_name)['logStreams']
    except logs.exceptions.ResourceNotFoundException:
        logger.info('Log group *{}* is not found.'.format(group_name))
        return 1
    stream_names = [obj['logStreamName'] for obj in streams]
    events = load_all_events(logs, name, group_name, stream_names)
    for event in events:
        print_event(event)
    return 0
