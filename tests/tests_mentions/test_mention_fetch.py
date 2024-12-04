from unittest.mock import patch
from tests.test_routes import BaseTestCase
from app.services.mention_services import MentionService, mention_service


class MentionTestCases(BaseTestCase):
    service: MentionService

    def setUp(self):
        super().setUp()
        self.service = mention_service

    @patch.object(MentionService, "get_mentions_by_document_edit")
    def test_get_mentions_by_document_edit_valid(self, get_mentions_mock):
        # Mocked response for the test
        get_mentions_mock.return_value = {"mentions": ["Mention 1", "Mention 2"]}, 200

        # Sending GET request with the document edit ID
        response = self.client.get("/api/mentions/1")

        # Check the response status code and data
        self.assertEqual(200, response.status_code)
        self.assertIn("mentions", response.json)
        self.assertEqual(response.json.get("mentions"), ["Mention 1", "Mention 2"])

    @patch.object(MentionService, "get_mentions_by_document_edit")
    def test_get_mentions_by_document_edit_not_found(self, get_mentions_mock):
        # Mock the service to raise a NotFound exception
        get_mentions_mock.return_value = {
            "message": "No mentions found for the given document edit."
        }, 404

        # Sending a GET request with a valid document_edit ID, but no mentions found
        response = self.client.get("/api/mentions/999")

        # Assert the response is 404
        self.assertEqual(404, response.status_code)
        self.assertEqual(
            response.json.get("message"),
            "No mentions found for the given document edit.",
        )

    @patch.object(MentionService, "get_mentions_by_document_edit")
    def test_get_mentions_by_document_edit_bad_request(self, get_mentions_mock):
        # Mock the service to simulate no service call (validation fails early)
        get_mentions_mock.return_value = None

        # Sending GET request with invalid document edit ID (non-integer)
        response = self.client.get("/api/mentions/abc")

        # Assert the response is 400 for bad input
        self.assertEqual(400, response.status_code)
        response_data = response.get_json()
        self.assertEqual(
            response_data.get("message"),
            "400 Bad Request: Document Edit ID must be a valid integer.",
        )
