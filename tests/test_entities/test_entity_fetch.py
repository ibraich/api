from unittest.mock import patch
from tests.test_routes import BaseTestCase
from app.services.entity_service import EntityService, entity_service


class TestEntityFetch(BaseTestCase):
    service = EntityService

    def setUp(self):
        super().setUp()
        self.service = entity_service

    @patch.object(EntityService, "get_entities_by_document_edit")
    def test_get_entities_by_document_edit_valid(self, get_entities_mock):
        # Mocked response for the test
        get_entities_mock.return_value = {"entities": ["entity 1", "entity 2"]}, 200

        # Sending GET request with the document edit ID
        response = self.client.get("/api/entities/1")

        # Check the response status code and data
        self.assertEqual(200, response.status_code)
        self.assertIn("entities", response.json)
        self.assertEqual(response.json.get("entities"), ["entity 1", "entity 2"])

    @patch.object(EntityService, "get_entities_by_document_edit")
    def test_get_entities_by_document_edit_not_found(self, get_entities_mock):
        # Mock the service to raise a NotFound exception
        get_entities_mock.return_value = {
            "message": "No entities found for the given document edit."
        }, 404

        # Sending a GET request with a valid document_edit ID, but no mentions found
        response = self.client.get("/api/entities/999")

        # Assert the response is 404
        self.assertEqual(404, response.status_code)
        self.assertEqual(
            response.json.get("message"),
            "No entities found for the given document edit.",
        )

    @patch.object(EntityService, "get_entities_by_document_edit")
    def test_get_entities_by_document_edit_bad_request(self, get_entities_mock):
        # Mock the service to simulate no service call (validation fails early)
        get_entities_mock.return_value = None

        # Sending GET request with invalid document edit ID (non-integer)
        response = self.client.get("/api/entities/abc")

        # Assert the response is 400 for bad input
        self.assertEqual(400, response.status_code)
        response_data = response.get_json()
        self.assertEqual(
            response_data.get("message"),
            "400 Bad Request: Document Edit ID must be a valid integer.",
        )
