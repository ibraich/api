from collections import namedtuple
from unittest.mock import patch

from werkzeug.exceptions import NotFound, BadRequestKeyError, BadRequest

from app.repositories.schema_repository import SchemaRepository
from app.services.schema_service import SchemaService, schema_service
from app.services.user_service import UserService
from tests.test_routes import BaseTestCase


class SchemaFetchIdTestCases(BaseTestCase):
    service: SchemaService

    def setUp(self):
        super().setUp()
        self.service = schema_service

    @patch.object(SchemaService, "get_schemas_by_user")
    def test_get_schema_by_user_endpoint_valid(self, get_schema_mock):
        # Mocked response for the test
        get_schema_mock.return_value = {
            "schemas": [
                {
                    "id": 1,
                    "is_fixed": False,
                    "modellingLanguage": "BPMN",
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_relations": [],
                    "schema_constraints": [],
                    "schema_mentions": [
                        {
                            "color": "blue",
                            "description": "desc",
                            "entity_possible": True,
                            "id": 1,
                            "tag": "tag",
                        }
                    ],
                }
            ]
        }

        response = self.client.get("/api/schemas/")

        # Check the response status code and data
        self.assertEqual(200, response.status_code)
        self.assertIn("schemas", response.json)
        self.assertEqual(
            response.json.get("schemas"),
            [
                {
                    "id": 1,
                    "is_fixed": False,
                    "modellingLanguage": "BPMN",
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_relations": [],
                    "schema_constraints": [],
                    "schema_mentions": [
                        {
                            "color": "blue",
                            "description": "desc",
                            "entity_possible": True,
                            "id": 1,
                            "tag": "tag",
                        }
                    ],
                }
            ],
        )

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(SchemaRepository, "get_schema_ids_by_user")
    def test_get_schema_by_user_no_schemas(self, get_schema_mock, get_user_mock):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1
        get_schema_mock.return_value = None

        response = self.client.get("/api/schemas/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual({"schemas": []}, response.json)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(SchemaRepository, "get_schema_ids_by_user")
    @patch.object(SchemaService, "get_schema_by_id")
    def test_get_schema_by_user_service_valid(
        self, get_schema_id_mock, get_schema_user_mock, get_user_mock
    ):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1

        schema_return = namedtuple(
            "Schema",
            ["id"],
        )
        get_schema_user_mock.return_value = [schema_return(1)]

        get_schema_id_mock.return_value = {
            "id": 1,
            "is_fixed": False,
            "modellingLanguage": "BPMN",
            "team_id": 1,
            "team_name": "Team1",
            "schema_relations": [],
            "schema_constraints": [],
            "schema_mentions": [
                {
                    "color": "blue",
                    "description": "desc",
                    "entity_possible": True,
                    "id": 1,
                    "tag": "tag",
                }
            ],
        }

        response = self.client.get("/api/schemas/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "schemas": [
                    {
                        "id": 1,
                        "is_fixed": False,
                        "modellingLanguage": "BPMN",
                        "team_id": 1,
                        "team_name": "Team1",
                        "schema_relations": [],
                        "schema_constraints": [],
                        "schema_mentions": [
                            {
                                "color": "blue",
                                "description": "desc",
                                "entity_possible": True,
                                "id": 1,
                                "tag": "tag",
                            }
                        ],
                    }
                ]
            },
            response.json,
        )
