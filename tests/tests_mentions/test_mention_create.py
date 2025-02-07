import unittest
from unittest.mock import patch
from app.models import Mention, Schema, SchemaMention

from app.services.mention_services import MentionService
from tests.test_routes import MentionBaseTestCase


class TestMentionCreateResource(MentionBaseTestCase):

    def setUp(self):
        super().setUp()

    @patch.object(MentionService, "check_token_in_mention")
    @patch.object(MentionService, "get_mention_dto_by_id")
    def test_create_mentions_success(
        self, get_dto_by_id_mock, check_token_in_mention_mock
    ):

        # Mock input data
        mock_doc_edit_id = 123
        moc_schema_mention_id = 456
        mock_token_ids = [1, 5, 9]

        check_token_in_mention_mock.return_value = []

        self.schema_service.get_schema_by_document_edit.return_value = Schema(id=9)
        self.schema_service.get_schema_mention_by_id.return_value = SchemaMention(
            id=6, schema_id=9
        )
        self.mention_repository.create_mention.return_value = Mention(id=4)
        get_dto_by_id_mock.return_value = {"id": 8}

        # Call the function
        response = self.service.create_mentions(
            mock_doc_edit_id, moc_schema_mention_id, mock_token_ids
        )

        # Assertions
        self.assertEqual(response, {"id": 8})
        self.token_mention_service.create_token_mention.assert_called()


if __name__ == "__main__":
    unittest.main()
