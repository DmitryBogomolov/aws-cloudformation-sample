import time
from datetime import timedelta
from .client import exceptions
from .text_painter import paint, colors
from .const import SOURCES_BUCKET

STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': colors.ORANGE,
    'CREATE_FAILED': colors.RED,
    'CREATE_COMPLETE': colors.GREEN,
    'ROLLBACK_IN_PROGRESS': colors.ORANGE,
    'ROLLBACK_FAILED': colors.RED,
    'ROLLBACK_COMPLETE': colors.GREEN,
    'DELETE_IN_PROGRESS': colors.ORANGE,
    'DELETE_FAILED': colors.RED,
    'DELETE_COMPLETE': colors.LIGHTGREY,
    'UPDATE_IN_PROGRESS': colors.ORANGE,
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': colors.ORANGE,
    'UPDATE_COMPLETE': colors.GREEN,
    'UPDATE_ROLLBACK_IN_PROGRESS': colors.RED,
    'UPDATE_ROLLBACK_FAILED': colors.RED,
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': colors.RED,
    'UPDATE_ROLLBACK_COMPLETE': colors.GREEN,
    'REVIEW_IN_PROGRESS': colors.LIGHTGREY
}

def get_stack_info(cf, stack_name):
    try:
        return cf.describe_stacks(StackName=stack_name)['Stacks'][0]
    except: # pylint: disable=bare-except
        return None

def is_stack_in_progress(stack):
    return stack['StackStatus'].endswith('_IN_PROGRESS')

def get_stack_events(cf, stack_name, timestamp):
    events = []
    args = {'StackName': stack_name}
    is_valid_event = lambda event: event['Timestamp'] > timestamp
    while True:
        # Stack may become deleted during request.
        try:
            response = cf.describe_stack_events(**args)
        except exceptions.ClientError:
            break
        batch = list(filter(is_valid_event, response['StackEvents']))
        events.extend(batch)
        token = response.get('NextToken')
        if token and batch:
            args['NextToken'] = token
        else:
            break
    return events

def watch_stack_status(cf, logger, stack_name):
    stack = get_stack_info(cf, stack_name)
    start_time = stack.get('LastUpdatedTime', stack['CreationTime'])
    event_timestamp = start_time - timedelta(seconds=1)
    align = lambda text: text[:31].ljust(32)
    errors = []

    while True:
        events = get_stack_events(cf, stack_name, event_timestamp)
        if events:
            event_timestamp = events[0]['Timestamp']
            for event in reversed(events):
                status = event['ResourceStatus']
                reason = event.get('ResourceStatusReason', '')
                logger.info(' '.join((
                    str((event['Timestamp'] - start_time).seconds).rjust(3),
                    paint(STATUS_TO_COLOR[status], align(status)),
                    align(event['ResourceType']),
                    align(event['LogicalResourceId']),
                    reason
                )))
                if status.endswith('_FAILED') and reason != 'Resource creation cancelled':
                    errors.append('{} {} {}'.format(
                        event['ResourceType'], event['LogicalResourceId'], reason))
        else:
            stack = get_stack_info(cf, stack_name)
            if not stack or not is_stack_in_progress(stack):
                break
        time.sleep(3)

    return ';'.join(errors) if errors else ''

def get_sources_bucket(cf, stack_name):
    outputs = get_stack_info(cf, stack_name)['Outputs']
    return next(obj['OutputValue'] for obj in outputs if obj['OutputKey'] == SOURCES_BUCKET)
