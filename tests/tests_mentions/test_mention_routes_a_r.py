import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestMentionRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.routes.mention_routes.mention_service")
    def test_accept_mention_success(self, mock_mention_service):
        mention_id = 1
        document_edit_id = 2
        mock_response = {"message": "Mention accepted"}

        # Mocking the service
        mock_mention_service.accept_mention.return_value = mock_response

        # Request
        response = self.client.post(
            f"/mentions/{mention_id}/accept",
            query_string={"document_edit_id": document_edit_id},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_response)
        mock_mention_service.accept_mention.assert_called_once_with(mention_id, document_edit_id)

    @patch("app.routes.mention_routes.mention_service")
    def test_accept_mention_missing_document_edit_id(self, mock_mention_service):
        mention_id = 1

        # Request without document_edit_id
        response = self.client.post(f"/mentions/{mention_id}/accept")

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])

    @patch("app.routes.mention_routes.mention_service")
    def test_reject_mention_success(self, mock_mention_service):
        mention_id = 1
        document_edit_id = 2
        mock_response = {"message": "Mention rejected"}

        # Mocking the service
        mock_mention_service.reject_mention.return_value = mock_response

        # Request
        response = self.client.post(
            f"/mentions/{mention_id}/reject",
            query_string={"document_edit_id": document_edit_id},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_response)
        mock_mention_service.reject_mention.assert_called_once_with(mention_id, document_edit_id)

    @patch("app.routes.mention_routes.mention_service")
    def test_reject_mention_missing_document_edit_id(self, mock_mention_service):
        mention_id = 1

        # Request without document_edit_id
        response = self.client.post(f"/mentions/{mention_id}/reject")

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])
