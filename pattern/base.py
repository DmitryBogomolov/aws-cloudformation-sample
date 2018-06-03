import yaml

class Base(object):
    TEMPLATE = None

    def __init__(self, source):
        self._source = source

    def get(self, name, default=None):
        value = self._source.get(name, default)
        if value is None:
            raise Exception('Field "{}" is not defined.'.format(name))
        return value

    def get_path(self, name):
        obj = self._source
        for item in name.split('.'):
            obj = obj.get(item)
        return obj

    def dump(self):
        template = yaml.load(self.TEMPLATE)
        self._dump(template)
        return template

    def _dump(self, template):
        raise Exception('Abstract')
