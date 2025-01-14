import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.routes.relation_routes.relation_service")
    def test_accept_relation_success(self, mock_relation_service):
        relation_id = 1
        document_edit_id = 2
        mock_response = {"message": "Relation accepted"}

        # Mocking the service
        mock_relation_service.accept_relation.return_value = mock_response

        # Request
        response = self.client.post(
            f"/relations/{relation_id}/accept",
            query_string={"document_edit_id": document_edit_id},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_response)
        mock_relation_service.accept_relation.assert_called_once_with(relation_id, document_edit_id)

    @patch("app.routes.relation_routes.relation_service")
    def test_accept_relation_missing_document_edit_id(self, mock_relation_service):
        relation_id = 1

        # Request without document_edit_id
        response = self.client.post(f"/relations/{relation_id}/accept")

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])

    @patch("app.routes.relation_routes.relation_service")
    def test_reject_relation_success(self, mock_relation_service):
        relation_id = 1
        document_edit_id = 2
        mock_response = {"message": "Relation rejected"}

        # Mocking the service
        mock_relation_service.reject_relation.return_value = mock_response

        # Request
        response = self.client.post(
            f"/relations/{relation_id}/reject",
            query_string={"document_edit_id": document_edit_id},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_response)
        mock_relation_service.reject_relation.assert_called_once_with(relation_id, document_edit_id)

    @patch("app.routes.relation_routes.relation_service")
    def test_reject_relation_missing_document_edit_id(self, mock_relation_service):
        relation_id = 1

        # Request without document_edit_id
        response = self.client.post(f"/relations/{relation_id}/reject")

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])
