import unittest
from unittest.mock import Mock
from app.services.mention_services import MentionService


class TestMentionService(unittest.TestCase):
    def setUp(self):
        # Mock the repository
        self.mock_repository = Mock()
        # Initialize the service with the mocked repository
        self.service = MentionService(self.mock_repository)

    def test_regenerate_mentions_success(self):
        # Mock the mention generation method
        self.service.generate_mentions = Mock(return_value=[{"data": "example mention"}])

        # Call the method
        mentions = self.service.regenerate_mentions(1)

        # Assertions
        self.service.generate_mentions.assert_called_once_with(1)
        self.mock_repository.delete_mentions.assert_called_once_with(1)
        self.mock_repository.add_mentions.assert_called_once_with(1, [{"data": "example mention"}])
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["data"], "example mention")

    def test_regenerate_mentions_no_mentions_generated(self):
        # Mock the mention generation to return an empty list
        self.service.generate_mentions = Mock(return_value=[])

        # Ensure an exception is raised
        with self.assertRaises(Exception) as context:
            self.service.regenerate_mentions(1)

        self.assertTrue("Could not generate mentions." in str(context.exception))
        self.service.generate_mentions.assert_called_once_with(1)
