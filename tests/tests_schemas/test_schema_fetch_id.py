from unittest.mock import patch

from werkzeug.exceptions import BadRequest

from app.repositories.schema_repository import SchemaRepository
from app.services.schema_service import SchemaService, schema_service
from app.services.user_service import UserService
from tests.test_routes import BaseTestCase


class SchemaFetchIdTestCases(BaseTestCase):
    service: SchemaService

    def setUp(self):
        super().setUp()
        self.service = schema_service

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(SchemaRepository, "get_schema_by_id")
    @patch.object(UserService, "check_user_schema_accessible")
    def test_get_schema_by_id_schema_invalid(
        self, check_schema_mock, get_schema_mock, get_user_mock
    ):
        # Mock the service to raise a BadRequest exception
        check_schema_mock.return_value = None
        get_user_mock.return_value = 1
        get_schema_mock.side_effect = BadRequest("Schema not found")

        # Sending a GET request with an invalid schema ID
        response = self.client.get("/api/schemas/999")

        # Assert the response is 400
        self.assertEqual(400, response.status_code)
