import boto3
from .helper import get_pattern_path
from .yaml import load

def make_session():
    kwargs = {}
    pattern = load(get_pattern_path())
    if 'profile' in pattern:
        kwargs['profile_name'] = pattern['profile']
    if 'region' in pattern:
        kwargs['region_name'] = pattern['region']
    return boto3.Session(**kwargs)

exceptions = boto3.exceptions.botocore.exceptions

class ClientProxy(object):
    _session = None

    def __init__(self, name):
        self._name = name
        self._target = None

    def __getattr__(self, name):
        self.__class__._session = self.__class__._session or make_session()
        self._target = self._target or self._session.client(self._name)
        return getattr(self._target, name)


proxies = {}

def client(name):
    proxy = proxies.get(name)
    if not proxy:
        proxy = ClientProxy(name)
        proxies[name] = proxy
    return proxy
