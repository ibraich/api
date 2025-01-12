import unittest
from unittest.mock import MagicMock
from services.mention_service import MentionService


class TestMentionService(unittest.TestCase):
    def setUp(self):
        self.service = MentionService()
        self.service.mention_repository = MagicMock()

    def test_accept_mention_success(self):
        self.service.mention_repository.get_mention_by_id.return_value = {"id": "mention123", "isShownRecommendation": True}
        self.service.accept_mention("mention123")
        self.service.mention_repository.create_in_document_edit.assert_called_once()
        self.service.mention_repository.update_is_shown.assert_called_once_with("mention123", False)

    def test_accept_mention_not_found(self):
        self.service.mention_repository.get_mention_by_id.return_value = None
        with self.assertRaises(Exception):
            self.service.accept_mention("invalid_id")

    def test_reject_mention_success(self):
        self.service.mention_repository.get_mention_by_id.return_value = {"id": "mention123", "isShownRecommendation": True}
        self.service.reject_mention("mention123")
        self.service.mention_repository.update_is_shown.assert_called_once_with("mention123", False)

    def test_reject_mention_not_found(self):
        self.service.mention_repository.get_mention_by_id.return_value = None
        with self.assertRaises(Exception):
            self.service.reject_mention("invalid_id")
