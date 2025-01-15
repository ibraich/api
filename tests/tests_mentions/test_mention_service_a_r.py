import unittest
from unittest.mock import MagicMock
from app.services.mention_services import mention_service, MentionService

class MentionServiceTests(unittest.TestCase):
    def setUp(self):
        self.mention_repository = MagicMock()
        self.mention_service = MentionService(self.mention_repository)

    def test_accept_recommendation(self):
        mention_data = {"id": 1, "content": "Test mention"}
        self.mention_repository.create.return_value = mention_data

        mention = self.mention_service.accept_recommendation(mention_data)
        self.mention_repository.create.assert_called_once_with(mention_data)
        self.assertFalse(mention["is_shown_recommendation"])

    def test_reject_recommendation(self):
        mention_data = {"id": 1, "content": "Test mention"}
        self.mention_repository.create.return_value = mention_data

        mention = self.mention_service.reject_recommendation(mention_data)
        self.mention_repository.create.assert_called_once_with(mention_data)
        self.assertFalse(mention["is_shown_recommendation"])
