class TestError(Exception):
    pass

def handler(event, content):
    raise TestError('Hello')
