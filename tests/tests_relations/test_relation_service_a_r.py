
import unittest
from unittest.mock import patch
from services.relation_service import RelationService

class TestRelationService(unittest.TestCase):
    def setUp(self):
        self.service = RelationService()

    @patch('repositories.relation_repository.RelationRepository.get_relation_by_id')
    @patch('repositories.relation_repository.RelationRepository.create_in_document_edit')
    @patch('repositories.relation_repository.RelationRepository.update_is_shown')
    def test_accept_relation_success(self, mock_update, mock_create, mock_get):
        mock_get.return_value = {"id": "relation123", "isShownRecommendation": True}
        self.service.accept_relation("relation123")
        mock_create.assert_called_once()
        mock_update.assert_called_once_with("relation123", False)

    @patch('repositories.relation_repository.RelationRepository.get_relation_by_id')
    def test_accept_relation_not_found(self, mock_get):
        mock_get.return_value = None
        with self.assertRaises(Exception) as context:
            self.service.accept_relation("invalid_id")
        self.assertIn("not found", str(context.exception))

    @patch('repositories.relation_repository.RelationRepository.get_relation_by_id')
    @patch('repositories.relation_repository.RelationRepository.update_is_shown')
    def test_reject_relation_success(self, mock_update, mock_get):
        mock_get.return_value = {"id": "relation123", "isShownRecommendation": True}
        self.service.reject_relation("relation123")
        mock_update.assert_called_once_with("relation123", False)
