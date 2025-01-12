import unittest
from unittest.mock import MagicMock
from services.relation_service import RelationService


class TestRelationService(unittest.TestCase):
    def setUp(self):
        self.service = RelationService()
        self.service.relation_repository = MagicMock()

    def test_accept_relation_success(self):
        self.service.relation_repository.get_relation_by_id.return_value = {"id": "relation123", "isShownRecommendation": True}
        self.service.accept_relation("relation123")
        self.service.relation_repository.create_in_document_edit.assert_called_once()
        self.service.relation_repository.update_is_shown.assert_called_once_with("relation123", False)

    def test_accept_relation_not_found(self):
        self.service.relation_repository.get_relation_by_id.return_value = None
        with self.assertRaises(Exception):
            self.service.accept_relation("invalid_id")

    def test_reject_relation_success(self):
        self.service.relation_repository.get_relation_by_id.return_value = {"id": "relation123", "isShownRecommendation": True}
        self.service.reject_relation("relation123")
        self.service.relation_repository.update_is_shown.assert_called_once_with("relation123", False)

    def test_reject_relation_not_found(self):
        self.service.relation_repository.get_relation_by_id.return_value = None
        with self.assertRaises(Exception):
            self.service.reject_relation("invalid_id")