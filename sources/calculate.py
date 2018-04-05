def handler(event, context):
    return float(event['a']) + float(event['b'])
