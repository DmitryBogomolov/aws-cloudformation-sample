from ..utils.loader import load_template
from .base import Base

class BaseResource(Base):
    def __init__(self, name, source, root):
        super().__init__(source)
        self.name = name
        self.root = root

    # pylint: disable=arguments-differ
    def dump(self, parent_template):
        template = load_template(self.TEMPLATE)
        self._dump(template, parent_template)
        parent_template['Resources'][self.name] = template

    # pylint: disable=unused-argument
    def _dump(self, template, parent_template):
        properties = template['Properties']
        properties.update(self.get('Properties', {}))

        # The following allows to avoid declaring "DependsOn: []" in every TEMPLATE field.
        depends_on = template.get('DependsOn')
        if not depends_on:
            depends_on = []
            template['DependsOn'] = depends_on
        depends_on.extend(self.get('DependsOn', []))
        depends_on.extend(self.get('depends_on', []))
        self._dump_properties(properties)


    def _dump_properties(self, properties):
        raise NotImplementedError('_dump_properties')
