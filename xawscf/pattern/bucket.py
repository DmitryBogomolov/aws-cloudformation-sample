from ..utils.loader import Custom
from ..utils.helper import set_tags_list, make_output
from .base_resource import BaseResource

class Bucket(BaseResource):
    TEMPLATE = \
'''
Type: AWS::S3::Bucket
Properties:
  Tags: []
'''

    TYPE = 'bucket'

    def _dump(self, template, parent_template):
        super()._dump(template, parent_template)
        name = self.name
        parent_template['Outputs'][name] = make_output(Custom('!Ref', name))
        parent_template['Outputs'][name + 'Url'] = make_output(
            Custom('!GetAtt', name + '.WebsiteURL'))

    def _dump_properties(self, properties):
        set_tags_list(properties, self)
