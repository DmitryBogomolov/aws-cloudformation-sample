import time
from datetime import datetime, timedelta
from .text_painter import paint, colors
from .const import SOURCES_BUCKET

STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': colors.ORANGE,
    'CREATE_COMPLETE': colors.GREEN,
    'CREATE_FAILED': colors.RED,
    'DELETE_IN_PROGRESS': colors.ORANGE,
    'UPDATE_IN_PROGRESS': colors.ORANGE,
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': colors.ORANGE,
    'DELETE_COMPLETE': colors.LIGHTGREY,
    'UPDATE_ROLLBACK_COMPLETE': colors.GREEN,
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': colors.RED,
    'UPDATE_ROLLBACK_IN_PROGRESS': colors.RED,
    'UPDATE_COMPLETE': colors.GREEN
}

def get_stack_info(cf, stack_name):
    response = cf.describe_stacks(StackName=stack_name)
    return response['Stacks'][0]

def is_stack_stable(cf, stack_name):
    return get_stack_info(cf, stack_name)['StackStatus'].endswith('_COMPLETE')

def get_stack_events(cf, stack_name, timestamp):
    events = []
    args = { 'StackName': stack_name }
    is_valid_event = lambda event: event['Timestamp'] > timestamp
    while True:
        response = cf.describe_stack_events(**args)
        batch = list(filter(is_valid_event, response['StackEvents']))
        events.extend(batch)
        token = response.get('NextToken')
        if token and len(batch) > 0:
            args['NextToken'] = token
        else:
            break
    return events

def watch_stack_status(cf, stack_name):
    stack = get_stack_info(cf, stack_name)
    if not stack['StackStatus'].endswith('_IN_PROGRESS'):
        return ''

    start_time = stack.get('LastUpdatedTime', stack['CreationTime'])
    event_timestamp = start_time - timedelta(seconds=1)
    align = lambda text: text[:31].ljust(32)
    errors = []

    while True:
        events = get_stack_events(cf, stack_name, event_timestamp)
        if len(events) > 0:
            event_timestamp = events[0]['Timestamp']
            for event in reversed(events):
                status = event['ResourceStatus']
                reason = event.get('ResourceStatusReason', '')
                # TODO: Use `log` here (after it is updated).
                print(str((event['Timestamp'] - start_time).seconds).rjust(3),
                    paint(STATUS_TO_COLOR.get(status, colors.RESET), align(status)),
                    align(event['ResourceType']), align(event['LogicalResourceId']),
                    reason)
                if status.endswith('_FAILED') and reason != 'Resource creation cancelled':
                    errors.append('{} {} {}'.format(
                        event['ResourceType'], event['LogicalResourceId'], reason))
        if is_stack_stable(cf, stack_name):
            break
        time.sleep(3)

    return ';'.join(errors) if len(errors) > 0 else ''

def get_sources_bucket(cf, stack_name):
    outputs = get_stack_info(cf, stack_name)['Outputs']
    return next(filter(lambda obj: obj['OutputKey'] == SOURCES_BUCKET, outputs))['OutputValue']
