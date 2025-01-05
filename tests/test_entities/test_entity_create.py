import unittest
from unittest.mock import patch, Mock
from werkzeug.exceptions import NotFound, BadRequest

from app.models import Mention
from app.repositories.entity_repository import EntityRepository
from app.repositories.mention_repository import MentionRepository
from app.services.entity_service import EntityService, entity_service
from app.services.user_service import UserService


class TestEntityServiceCreateEntity(unittest.TestCase):
    service: EntityService

    def setUp(self):
        super().setUp()
        self.service = entity_service

    @patch.object(MentionRepository, "get_mention_by_id")
    @patch.object(MentionRepository, "save_mention")
    @patch.object(EntityRepository, "create_entity")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    def test_create_entity_success(
        self,
        mock_get_user_by_document_edit_id,
        mock_get_logged_in_user_id,
        mock_create_entity,
        mock_save_mention,
        mock_get_mention_by_id,
    ):
        # Input data for the test
        mock_data = {
            "document_edit_id": 123,
            "mention_ids": [1, 2],
        }

        # Mock the user validation
        mock_get_logged_in_user_id.return_value = 1
        mock_get_user_by_document_edit_id.return_value = 1

        # Mock mentions
        mention1 = Mock(tag="TagA", id=1, entity_id=None)
        mention2 = Mock(tag="TagA", id=2, entity_id=None)
        mock_get_mention_by_id.side_effect = [mention1, mention2]

        # Mock entity creation
        mock_entity = Mock(
            id=101,
            isShownRecommendation=True,
            document_edit_id=123,
            document_recommendation_id=42,
        )
        mock_create_entity.return_value = mock_entity

        # Call the method
        response = self.service.create_entity(mock_data)

        # Assertions
        self.assertEqual(response["id"], 101)
        self.assertTrue(response["isShownRecommendation"])
        self.assertEqual(response["document_edit_id"], 123)
        self.assertEqual(response["document_recommendation_id"], 42)

        # Verify method calls
        mock_get_logged_in_user_id.assert_called_once()
        mock_get_user_by_document_edit_id.assert_called_once_with(123)
        mock_get_mention_by_id.assert_any_call(1)
        mock_get_mention_by_id.assert_any_call(2)
        mock_create_entity.assert_called_once_with(123)
        mock_save_mention.assert_called_once()

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    def test_create_entity_unauthorized(
        self, mock_get_user_by_document_edit_id, mock_get_logged_in_user_id
    ):
        # Input data for the test
        mock_data = {
            "document_edit_id": 123,
            "mention_ids": [1, 2],
        }

        # Mock user validation failure
        mock_get_logged_in_user_id.return_value = 1
        mock_get_user_by_document_edit_id.return_value = 2

        # Expect NotFound exception
        with self.assertRaises(NotFound):
            self.service.create_entity(mock_data)

        # Verify method calls
        mock_get_logged_in_user_id.assert_called_once()
        mock_get_user_by_document_edit_id.assert_called_once_with(123)

    @patch.object(MentionRepository, "get_mention_by_id")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    def test_create_entity_multiple_tags(
        self,
        mock_get_user_by_document_edit_id,
        mock_get_logged_in_user_id,
        mock_get_mention_by_id,
    ):
        # Input data for the test
        mock_data = {
            "document_edit_id": 123,
            "mention_ids": [1, 2],
        }

        # Mock user validation
        mock_get_logged_in_user_id.return_value = 1
        mock_get_user_by_document_edit_id.return_value = 1

        # Mock mentions with multiple tags
        mention1 = Mention(tag="TagA", id=1, entity_id=None)
        mention2 = Mention(tag="TagB", id=2, entity_id=None)
        mock_get_mention_by_id.side_effect = [mention1, mention2]

        # Expect BadRequest exception
        with self.assertRaises(BadRequest):
            self.service.create_entity(mock_data)

        # Verify method calls
        mock_get_logged_in_user_id.assert_called_once()
        mock_get_user_by_document_edit_id.assert_called_once_with(123)
        mock_get_mention_by_id.assert_any_call(1)
        mock_get_mention_by_id.assert_any_call(2)


if __name__ == "__main__":
    unittest.main()
