import unittest
from unittest.mock import Mock
from app.services.relation_services import RelationService

class TestRelationEndpoint(unittest.TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.service = RelationService(self.mock_repository)

    def test_regenerate_relations_success(self):
        self.service.generate_relations = Mock(return_value=[{"data": "example"}])
        relations = self.service.regenerate_relations(1)
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["data"], "example")

    def test_no_relations_generated(self):
        self.service.generate_relations = Mock(return_value=[])
        with self.assertRaises(RuntimeError):
            self.service.regenerate_relations(1)
