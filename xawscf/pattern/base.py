from ..utils.loader import load_template

DEFAULT = object()

class Base:
    TEMPLATE = None

    def __init__(self, source):
        self._source = source

    def get(self, name, default=DEFAULT):
        value = self._source.get(name)
        if value is None:
            if default is DEFAULT:
                raise KeyError('Field "{}" is not defined.'.format(name))
            return default
        return value

    def get_path(self, name, default=DEFAULT):
        obj = self._source
        for item in name.split('.'):
            obj = obj.get(item)
            if obj is None:
                if default is DEFAULT:
                    raise KeyError('Field "{}" in "{}" is not defined.'.format(item, name))
                return default
        return obj

    def dump(self):
        template = load_template(self.TEMPLATE)
        self._dump(template)
        return template

    def _dump(self, template):
        raise NotImplementedError('_dump')
