from unittest.mock import patch, Mock

from werkzeug.exceptions import BadRequest

from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.user_service import UserService
from tests.test_routes import BaseTestCase
from app.services.document_edit_service import (
    DocumentEditService,
    document_edit_service,
)


class DocumentEditOvertakeTestCases(BaseTestCase):
    service: DocumentEditService

    def setUp(self):
        super().setUp()
        self.service = document_edit_service

    @patch.object(DocumentEditRepository, "get_document_edit_by_id")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    @patch.object(UserService, "get_logged_in_user_team_id")
    @patch.object(DocumentEditService, "get_document_edit_by_document")
    @patch.object(DocumentEditRepository, "store_object")
    def test_overtake_document_edit_success(
        self,
        mock_store_object,
        mock_get_document_edit_by_document,
        mock_get_logged_in_user_team_id,
        mock_get_user_by_document_edit_id,
        mock_get_logged_in_user_id,
        mock_get_document_edit_by_id,
    ):
        # Mock document edit object
        mock_document_edit = Mock()
        mock_document_edit.id = 123
        mock_document_edit.user_id = 2
        mock_document_edit.document_id = 456
        mock_document_edit.schema_id = 789

        mock_document_edit_return = Mock()
        mock_document_edit_return.id = 123
        mock_document_edit_return.user_id = 1
        mock_document_edit_return.document_id = 456
        mock_document_edit_return.schema_id = 789

        # Mock existing methods
        mock_store_object.return_value = mock_document_edit_return
        mock_get_document_edit_by_id.return_value = mock_document_edit
        mock_get_logged_in_user_id.return_value = 1  # New user ID
        mock_get_user_by_document_edit_id.return_value = Mock(team_id=100)
        mock_get_logged_in_user_team_id.return_value = 100
        mock_get_document_edit_by_document.return_value = (
            None  # No existing edit for user
        )

        # Call the function
        response = self.service.overtake_document_edit(123)

        # Assertions
        self.assertEqual(response["id"], 123)
        self.assertEqual(response["schema_id"], 789)
        self.assertEqual(response["document_id"], 456)

        # Verify repository calls
        mock_get_document_edit_by_id.assert_called_once_with(123)
        mock_get_logged_in_user_id.assert_called_once()
        mock_get_user_by_document_edit_id.assert_called_once_with(123)
        mock_get_logged_in_user_team_id.assert_called_once()

    @patch.object(DocumentEditRepository, "get_document_edit_by_id")
    def test_overtake_document_edit_not_found(self, mock_get_document_edit_by_id):
        # Document edit does not exist
        mock_get_document_edit_by_id.return_value = None

        with self.assertRaises(BadRequest) as context:
            self.service.overtake_document_edit(123)

        # Assertion
        self.assertEqual(
            str(context.exception), "400 Bad Request: Document edit does not exist"
        )
        mock_get_document_edit_by_id.assert_called_once_with(123)

    @patch.object(DocumentEditRepository, "get_document_edit_by_id")
    @patch.object(UserService, "get_logged_in_user_id")
    def test_overtake_document_edit_already_owner(
        self, mock_get_logged_in_user_id, mock_get_document_edit_by_id
    ):
        # Mock document edit object
        mock_document_edit = Mock()
        mock_document_edit.user_id = 1  # Same as logged-in user
        mock_get_document_edit_by_id.return_value = mock_document_edit
        mock_get_logged_in_user_id.return_value = 1

        with self.assertRaises(BadRequest) as context:
            self.service.overtake_document_edit(123)

        # Assertion
        self.assertEqual(
            str(context.exception),
            "400 Bad Request: User already has access to this document edit",
        )
        mock_get_document_edit_by_id.assert_called_once_with(123)
        mock_get_logged_in_user_id.assert_called_once()

    @patch.object(DocumentEditRepository, "get_document_edit_by_id")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    @patch.object(UserService, "get_logged_in_user_team_id")
    def test_overtake_document_edit_no_team_access(
        self,
        mock_get_logged_in_user_team_id,
        mock_get_user_by_document_edit_id,
        mock_get_logged_in_user_id,
        mock_get_document_edit_by_id,
    ):
        # Mock document edit object
        mock_document_edit = Mock()
        mock_document_edit.id = 123
        mock_document_edit.user_id = 2

        mock_get_document_edit_by_id.return_value = mock_document_edit
        mock_get_logged_in_user_id.return_value = 1  # New user ID
        mock_get_user_by_document_edit_id.return_value = Mock(team_id=100)
        mock_get_logged_in_user_team_id.return_value = 100
        mock_get_logged_in_user_team_id.return_value = 200  # Different team

        with self.assertRaises(BadRequest) as context:
            self.service.overtake_document_edit(123)

        # Assertion
        self.assertEqual(
            str(context.exception),
            "400 Bad Request: User does not have access to this document edit",
        )

    @patch.object(DocumentEditRepository, "get_document_edit_by_id")
    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "get_user_by_document_edit_id")
    @patch.object(UserService, "get_logged_in_user_team_id")
    @patch.object(DocumentEditService, "get_document_edit_by_document")
    def test_overtake_document_edit_already_exists_for_user(
        self,
        mock_get_document_edit_by_document,
        mock_get_logged_in_user_team_id,
        mock_get_user_by_document_edit_id,
        mock_get_logged_in_user_id,
        mock_get_document_edit_by_id,
    ):
        # Mock document edit object
        mock_document_edit = Mock()
        mock_document_edit.document_id = 456

        mock_get_document_edit_by_id.return_value = mock_document_edit
        mock_get_logged_in_user_id.return_value = 1
        mock_get_document_edit_by_document.return_value = Mock()
        mock_get_user_by_document_edit_id.return_value = Mock(team_id=100)
        mock_get_logged_in_user_team_id.return_value = 100
        with self.assertRaises(BadRequest) as context:
            self.service.overtake_document_edit(123)

        # Assertion
        self.assertEqual(
            str(context.exception), "400 Bad Request: Document edit already exists"
        )
