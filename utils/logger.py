def log(message, *args, **kwargs):
    print(message.format(*args, **kwargs))

def logError(err):
    print(err)
