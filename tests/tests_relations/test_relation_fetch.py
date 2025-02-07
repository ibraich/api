import json
from unittest.mock import patch

from werkzeug.exceptions import NotFound

from app.services.relation_services import RelationService, relation_service
from app.db import db
from tests.test_routes import BaseTestCase


class RelationTestCases(BaseTestCase):
    service: RelationService

    def setUp(self):
        super().setUp()
        self.service = relation_service

    @patch.object(RelationService, "get_relations_by_document_edit")
    def test_get_relations_by_document_edit_bad_request(self, get_relations_mock):
        # Mock the service to simulate no service call (validation fails early)
        get_relations_mock.return_value = None

        # Sending GET request with invalid document_edit ID (non-integer)
        response = self.client.get("/api/relations/abc")

        # Assert the response is 404
        self.assertEqual(404, response.status_code)
