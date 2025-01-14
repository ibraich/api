import unittest
from unittest.mock import Mock
from app.services.mention_services import MentionService

class TestMentionEndpoint(unittest.TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.service = MentionService(self.mock_repository)

    def test_regenerate_mentions_success(self):
        self.service.generate_mentions = Mock(return_value=[{"data": "example"}])
        mentions = self.service.regenerate_mentions(1)
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["data"], "example")

    def test_no_mentions_generated(self):
        self.service.generate_mentions = Mock(return_value=[])
        with self.assertRaises(RuntimeError):
            self.service.regenerate_mentions(1)
