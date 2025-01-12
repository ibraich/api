
import unittest
from unittest.mock import patch
from services.mention_service import MentionService

class TestMentionService(unittest.TestCase):
    def setUp(self):
        self.service = MentionService()

    @patch('repositories.mention_repository.MentionRepository.get_mention_by_id')
    @patch('repositories.mention_repository.MentionRepository.create_in_document_edit')
    @patch('repositories.mention_repository.MentionRepository.update_is_shown')
    def test_accept_mention_success(self, mock_update, mock_create, mock_get):
        mock_get.return_value = {"id": "mention123", "isShownRecommendation": True}
        self.service.accept_mention("mention123")
        mock_create.assert_called_once()
        mock_update.assert_called_once_with("mention123", False)

    @patch('repositories.mention_repository.MentionRepository.get_mention_by_id')
    def test_accept_mention_not_found(self, mock_get):
        mock_get.return_value = None
        with self.assertRaises(Exception) as context:
            self.service.accept_mention("invalid_id")
        self.assertIn("not found", str(context.exception))

    @patch('repositories.mention_repository.MentionRepository.get_mention_by_id')
    @patch('repositories.mention_repository.MentionRepository.update_is_shown')
    def test_reject_mention_success(self, mock_update, mock_get):
        mock_get.return_value = {"id": "mention123", "isShownRecommendation": True}
        self.service.reject_mention("mention123")
        mock_update.assert_called_once_with("mention123", False)
