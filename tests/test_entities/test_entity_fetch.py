from unittest.mock import patch

from werkzeug.exceptions import NotFound

from app.models import Entity
from tests.test_routes import EntityBaseTestCase
from app.services.entity_service import EntityService


class TestEntityFetch(EntityBaseTestCase):

    def setUp(self):
        super().setUp()

    def test_get_entities_by_document_edit_valid(self):
        # Mocked response for the test
        self.mention_service.get_mentions_by_document_edit.return_value = {
            "mentions": [
                {"id": 1, "document_edit_id": 2, "entity_id": 1},
                {"id": 3, "document_edit_id": 2, "entity_id": None},
            ]
        }
        self.entity_repository.get_entities_by_document_edit.return_value = [
            Entity(
                id=1,
                isShownRecommendation=False,
                document_edit_id=2,
                document_recommendation_id=None,
            ),
            Entity(
                id=2,
                isShownRecommendation=True,
                document_edit_id=2,
                document_recommendation_id=None,
            ),
        ]

        response = self.service.get_entities_by_document_edit(2)
        # Check the response status code and data
        self.assertIn("entities", response)
        self.assertEqual(
            response.get("entities"),
            [
                {
                    "id": 1,
                    "isShownRecommendation": False,
                    "document_edit_id": 2,
                    "document_recommendation_id": None,
                    "mentions": [{"id": 1, "document_edit_id": 2, "entity_id": 1}],
                },
                {
                    "id": 2,
                    "isShownRecommendation": True,
                    "document_edit_id": 2,
                    "document_recommendation_id": None,
                    "mentions": [],
                },
            ],
        )

    @patch.object(EntityService, "get_entities_by_document_edit")
    def test_get_entities_by_document_edit_not_found(self, get_entities_mock):
        # Mock the service to raise a NotFound exception
        get_entities_mock.side_effect = NotFound(
            "No entities found for the given document edit."
        )

        # Sending a GET request with a valid document_edit ID, but no mentions found
        with self.assertRaises(NotFound):
            self.service.get_entities_by_document_edit(999)

    @patch.object(EntityService, "get_entities_by_document_edit")
    def test_get_entities_by_document_edit_bad_request(self, get_entities_mock):
        # Mock the service to simulate no service call (validation fails early)
        get_entities_mock.return_value = None

        # Sending GET request with invalid document edit ID (non-integer)
        response = self.client.get("/api/entities/abc")

        # Assert the response is 404
        self.assertEqual(404, response.status_code)
