import unittest
from unittest.mock import Mock
from app.services.relation_services import RelationService


class TestRelationService(unittest.TestCase):
    def setUp(self):
        # Mock the repository
        self.mock_repository = Mock()
        # Initialize the service with the mocked repository
        self.service = RelationService(self.mock_repository)

    def test_regenerate_relations_success(self):
        # Mock the relation generation method
        self.service.generate_relations = Mock(return_value=[{"data": "example relation"}])

        # Call the method
        relations = self.service.regenerate_relations(1)

        # Assertions
        self.service.generate_relations.assert_called_once_with(1)
        self.mock_repository.delete_relations.assert_called_once_with(1)
        self.mock_repository.add_relations.assert_called_once_with(1, [{"data": "example relation"}])
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0]["data"], "example relation")

    def test_regenerate_relations_no_relations_generated(self):
        # Mock the relation generation to return an empty list
        self.service.generate_relations = Mock(return_value=[])

        # Ensure an exception is raised
        with self.assertRaises(Exception) as context:
            self.service.regenerate_relations(1)

        self.assertTrue("Could not generate relations." in str(context.exception))
        self.service.generate_relations.assert_called_once_with(1)
