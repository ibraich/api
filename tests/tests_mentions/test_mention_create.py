import unittest
from unittest.mock import patch, Mock
from werkzeug.exceptions import NotFound, Conflict
from app.models import Mention

from app.repositories.mention_repository import MentionRepository
from app.services.document_edit_service import DocumentEditService
from app.services.mention_services import MentionService, mention_service
from app.services.token_mention_service import TokenMentionService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from tests.test_routes import BaseTestCase


class TestMentionResource(BaseTestCase):
    service: MentionService

    def setUp(self):
        super().setUp()
        self.service = mention_service

    @patch.object(MentionRepository, "create_mention")
    @patch.object(MentionService, "check_token_in_mention")
    @patch.object(UserService, "check_user_document_edit_accessible")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(TokenService, "check_tokens_in_document_edit")
    @patch.object(TokenMentionService, "create_token_mention")
    def test_create_mentions_success(
        self,
        mock_create_token_mention,
        mock_get_mentions_by_document_edit,
        mock_get_logged_in_user_id,
        mock_check_docedit,
        mock_get_token_mention,
        mock_create_mention,
    ):

        # Mock input data
        mock_input_data = {
            "tag": "string",
            "document_edit_id": 123,
            "token_ids": [],
        }

        # Mock services
        mock_create_token_mention.return_value = None
        mock_get_mentions_by_document_edit.return_value = []
        mock_get_logged_in_user_id.return_value = 1
        mock_check_docedit.return_value = 1  # Same user
        mock_get_token_mention.return_value = []  # No duplicates
        mock_create_mention.return_value = {
            "id": 1,
            "document_edit_id": 123,
            "tag": "sample_tag",
            "entity_id": 789,
        }, 200  # Created mention

        # Call the function
        response, status_code = self.service.create_mentions(mock_input_data)

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response["id"], 1)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    def test_create_mentions_not_authorized(self, get_user_id, get_logged_in_user_id):
        # Mock input data
        mock_input_data = {
            "tag": "string",
            "document_edit_id": 123,
            "token_ids": [1, 2, 3],
        }

        # Mock services
        get_logged_in_user_id.return_value = 1
        get_user_id.return_value = 2  # Different user

        # Test and assert NotFound exception
        with self.assertRaises(NotFound):
            self.service.create_mentions(mock_input_data)

        # Verify methods were called
        get_logged_in_user_id.assert_called_once()
        get_user_id.assert_called_once_with(123)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "check_user_document_edit_accessible")
    @patch.object(TokenService, "check_tokens_in_document_edit")
    @patch.object(MentionService, "check_token_in_mention")
    def test_create_mentions_duplicate_tokens(
        self,
        check_token_in_mention,
        check_tokens_in_document_edit,
        check_user_document_edit_accessible,
        get_logged_in_user_id,
    ):
        # Mock input data
        mock_input_data = {
            "tag": "string",
            "document_edit_id": 123,
            "token_ids": [1, 2, 3],
        }

        # Mock services
        get_logged_in_user_id.return_value = 1
        check_user_document_edit_accessible.return_value = 1  # Simulate same user
        check_token_in_mention.side_effect = ["exists", "duplicate"]

        mock_mention_1 = Mock()
        mock_mention_1.id = 2
        mock_mention_1.document_edit_id = 123
        mock_mention_1.tag = "sample_tag"
        mock_mention_1.entity_id = 789

        mock_mention_2 = Mock()
        mock_mention_2.id = 4
        mock_mention_2.document_edit_id = 1234
        mock_mention_2.tag = "sample_tag"
        mock_mention_2.entity_id = 789

        check_tokens_in_document_edit.return_value = None
        with self.assertRaises(Conflict):
            self.service.create_mentions(mock_input_data)

        # Verify methods were called
        get_logged_in_user_id.assert_called_once()
        check_user_document_edit_accessible.assert_called_once_with(1, 123)


if __name__ == "__main__":
    unittest.main()
