import unittest
from unittest.mock import patch, Mock, MagicMock
from werkzeug.exceptions import NotFound, Conflict
from app.models import Mention, Schema, SchemaMention

from app.repositories.mention_repository import MentionRepository
from app.services.document_edit_service import DocumentEditService
from app.services.entity_mention_service import EntityMentionService
from app.services.mention_services import MentionService, mention_service
from app.services.relation_mention_service import RelationMentionService
from app.services.schema_service import SchemaService
from app.services.token_mention_service import TokenMentionService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from tests.test_routes import BaseTestCase


class TestMentionResource(BaseTestCase):
    service: MentionService

    def setUp(self):
        super().setUp()
        self.__mention_repository = MagicMock(spec=MentionRepository)
        self.token_mention_service = MagicMock(spec=TokenMentionService)
        self.user_service = MagicMock(spec=UserService)
        self.relation_mention_service = MagicMock(spec=RelationMentionService)
        self.entity_mention_service = MagicMock(spec=EntityMentionService)
        self.token_service = MagicMock(spec=TokenService)
        self.schema_service = MagicMock(spec=SchemaService)
        self.service = MentionService(
            self.__mention_repository,
            self.token_mention_service,
            self.user_service,
            self.relation_mention_service,
            self.entity_mention_service,
            self.token_service,
            self.schema_service,
        )

    @patch.object(MentionService, "check_token_in_mention")
    @patch.object(MentionService, "get_mention_dto_by_id")
    def test_create_mentions_success(
        self, get_dto_by_id_mock, check_token_in_mention_mock
    ):

        # Mock input data
        mock_doc_edit_id = 123
        moc_schema_mention_id = 456
        mock_token_ids = [1, 5, 9]

        self.schema_service.get_schema_by_document_edit.return_value = Schema(id=9)
        self.schema_service.get_schema_mention_by_id.return_value = SchemaMention(
            id=6, schema_id=9
        )
        self.__mention_repository.create_mention.return_value = Mention(id=4)
        get_dto_by_id_mock.return_value = {"id": 8}

        # Call the function
        response = self.service.create_mentions(
            mock_doc_edit_id, moc_schema_mention_id, mock_token_ids
        )

        # Assertions
        self.assertEqual(response, {"id": 8})
        self.token_mention_service.create_token_mention.assert_called()

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
