def log(message, *args, **kwargs):
    entry = message
    if len(args) + len(kwargs) > 0:
        entry = message.format(*args, **kwargs)
    print(entry)

def logError(err):
    print(err)
