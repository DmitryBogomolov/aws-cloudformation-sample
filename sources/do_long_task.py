import threading

def calculate(context):
    context['result'] = float(context['a']) + float(context['b'])

def handler(event, context):
    ctx = event.copy()
    thread = threading.Timer(5, calculate, args=[ctx])
    print('begin')
    thread.start()
    thread.join()
    print('end')
    return ctx['result']
