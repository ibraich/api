import unittest
from unittest.mock import MagicMock
from app.services.relation_services import relation_service, RelationService

class RelationServiceTests(unittest.TestCase):
    def setUp(self):
        self.relation_repository = MagicMock()
        self.relation_service = RelationService(self.relation_repository)

    def test_accept_recommendation(self):
        relation_data = {"id": 1, "content": "Test relation"}
        self.relation_repository.create.return_value = relation_data

        relation = self.relation_service.accept_recommendation(relation_data)
        self.relation_repository.create.assert_called_once_with(relation_data)
        self.assertFalse(relation["is_shown_recommendation"])

    def test_reject_recommendation(self):
        relation_data = {"id": 1, "content": "Test relation"}
        self.relation_repository.create.return_value = relation_data

        relation = self.relation_service.reject_recommendation(relation_data)
        self.relation_repository.create.assert_called_once_with(relation_data)
        self.assertFalse(relation["is_shown_recommendation"])
