import unittest
from .. import apigateway
from ...utils.loader import Custom

class TestApiGateway(unittest.TestCase):
    def test_get_resource(self):
        resources = { '': { 'name': '' } }
        apigateway.get_resource('/a/b', resources)
        apigateway.get_resource('/a/b/{proxy+}', resources)
        apigateway.get_resource('/a/{c}/{d}', resources)

        self.assertEqual(resources, {
            '': { 'name': '' },
            '/a': { 'name': 'A', 'parent': '', 'part': 'a' },
            '/a/b': { 'name': 'AB', 'parent': '/a', 'part': 'b' },
            '/a/b/{proxy+}': { 'name': 'ABProxyVar', 'parent': '/a/b', 'part': '{proxy+}' },
            '/a/{c}': { 'name': 'ACVar', 'parent': '/a', 'part': '{c}' },
            '/a/{c}/{d}': { 'name': 'ACVarDVar', 'parent': '/a/{c}', 'part': '{d}' }
        })

    def test_build_resource_id(self):
        self.assertEqual(apigateway.build_resource_id('', 'Api1'),
            Custom('!GetAtt', 'Api1.RootResourceId'))
        self.assertEqual(apigateway.build_resource_id('Name1', 'Api1'),
            Custom('!Ref', 'Api1ResourceName1'))
