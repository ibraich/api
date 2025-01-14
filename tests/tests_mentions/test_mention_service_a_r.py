import unittest
from unittest.mock import MagicMock
from app.services.mention_services import MentionService

class TestMentionService(unittest.TestCase):
    def setUp(self):
        self.mention_repository = MagicMock()
        self.mention_service = MentionService(self.mention_repository)

    def test_accept_mention_success(self):
        # Mock-Daten
        mention_id = 1
        document_edit_id = 2
        mention_mock = MagicMock(
            id=mention_id,
            document_edit_id=document_edit_id,
            isShownRecommendation=True,
            tag="test-tag"
        )

        self.mention_repository.get_mention_by_id.return_value = mention_mock

        # Test
        result = self.mention_service.accept_mention(mention_id, document_edit_id)

        # Assertions
        self.mention_repository.get_mention_by_id.assert_called_once_with(mention_id)
        self.mention_repository.create_mention.assert_called_once_with(
            tag="test-tag",
            document_edit_id=document_edit_id,
            document_recommendation_id=None,
            is_shown_recommendation=False,
        )
        self.mention_repository.update_is_shown_recommendation.assert_called_once_with(mention_id, False)
        self.assertIsNotNone(result)

    def test_accept_mention_invalid_document_edit_id(self):
        mention_id = 1
        document_edit_id = 2
        mention_mock = MagicMock(id=mention_id, document_edit_id=99, isShownRecommendation=True)

        self.mention_repository.get_mention_by_id.return_value = mention_mock

        with self.assertRaises(ValueError):
            self.mention_service.accept_mention(mention_id, document_edit_id)

    def test_reject_mention_success(self):
        # Mock-Daten
        mention_id = 1
        document_edit_id = 2
        mention_mock = MagicMock(
            id=mention_id,
            document_edit_id=document_edit_id,
            isShownRecommendation=True
        )

        self.mention_repository.get_mention_by_id.return_value = mention_mock

        # Test
        result = self.mention_service.reject_mention(mention_id, document_edit_id)

        # Assertions
        self.mention_repository.get_mention_by_id.assert_called_once_with(mention_id)
        self.mention_repository.update_is_shown_recommendation.assert_called_once_with(mention_id, False)
        self.assertIsNotNone(result)

    def test_reject_mention_invalid_state(self):
        mention_id = 1
        document_edit_id = 2
        mention_mock = MagicMock(id=mention_id, document_edit_id=document_edit_id, isShownRecommendation=False)

        self.mention_repository.get_mention_by_id.return_value = mention_mock

        with self.assertRaises(ValueError):
            self.mention_service.reject_mention(mention_id, document_edit_id)
