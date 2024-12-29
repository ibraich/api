from collections import namedtuple
from unittest.mock import patch

from werkzeug.exceptions import NotFound, BadRequestKeyError, BadRequest

from app.repositories.schema_repository import SchemaRepository
from app.services.schema_service import SchemaService, schema_service
from tests.test_routes import BaseTestCase


class SchemaFetchIdTestCases(BaseTestCase):
    service: SchemaService

    def setUp(self):
        super().setUp()
        self.service = schema_service

    @patch.object(SchemaService, "get_schema_by_id")
    def test_get_schema_by_id_endpoint_valid(self, get_schema_mock):
        # Mocked response for the test
        get_schema_mock.return_value = {
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

        # Sending GET request with the schema ID
        response = self.client.get("/api/schemas/1")

        # Check the response status code and data
        self.assertEqual(200, response.status_code)
        self.assertIn("schema_mentions", response.json)
        self.assertEqual(
            response.json.get("schema_mentions"),
            [
                {
                    "color": "blue",
                    "description": "desc",
                    "entity_possible": True,
                    "id": 1,
                    "tag": "tag",
                }
            ],
        )

    @patch.object(SchemaRepository, "get_schema_by_id")
    def test_get_schema_by_id_schema_invalid(self, get_schema_mock):
        # Mock the service to raise a BadRequest exception
        get_schema_mock.side_effect = BadRequest("Schema not found")

        # Sending a GET request with an invalid schema ID
        response = self.client.get("/api/schemas/999")

        # Assert the response is 400
        self.assertEqual(400, response.status_code)

    @patch.object(SchemaRepository, "get_schema_by_id")
    @patch.object(SchemaRepository, "get_schema_constraints_by_schema")
    @patch.object(SchemaRepository, "get_schema_mentions_by_schema")
    @patch.object(SchemaRepository, "get_schema_relations_by_schema")
    def test_get_schema_by_id_service_valid(
        self, get_relation_mock, get_mention_mock, get_constraint_mock, get_schema_mock
    ):

        # Mock SQL-Alchemy return objects
        constraint_return = namedtuple(
            "Constraint",
            [
                "id",
                "isDirected",
                "relation_id",
                "relation_tag",
                "relation_description",
                "mention_head_id",
                "mention_tail_id",
                "mention_head_tag",
                "mention_tail_tag",
                "mention_head_description",
                "mention_tail_description",
                "mention_head_color",
                "mention_tail_color",
                "mention_head_entityPossible",
                "mention_tail_entityPossible",
            ],
        )

        relation_return = namedtuple("Relation", ["id", "tag", "description"])
        mention_return = namedtuple(
            "Mention", ["id", "tag", "description", "color", "entityPossible"]
        )
        schema_return = namedtuple(
            "Schema",
            ["id", "isFixed", "modelling_language", "team_id", "team_name"],
        )

        get_constraint_mock.return_value = [
            constraint_return(
                1,
                True,
                1,
                "relation_tag",
                "relation_description",
                1,
                2,
                "mention_head_tag",
                "mention_tail_tag",
                "mention_head_description",
                "mention_tail_description",
                "mention_head_color",
                "mention_tail_color",
                True,
                False,
            )
        ]

        get_relation_mock.return_value = [
            relation_return(
                1,
                "tag1",
                "description1",
            )
        ]

        get_mention_mock.return_value = [
            mention_return(
                1,
                "tag1",
                "description1",
                "blue",
                False,
            )
        ]

        get_schema_mock.return_value = schema_return(
            1,
            True,
            "BPMN",
            1,
            "Team1",
        )
        # Sending GET request with valid schema ID
        response = self.client.get("/api/schemas/1")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)

        # Assert returned object contains required fields
        self.assertEqual(
            response.json,
            {
                "id": 1,
                "is_fixed": True,
                "modellingLanguage": "BPMN",
                "team_id": 1,
                "team_name": "Team1",
                "schema_mentions": [
                    {
                        "id": 1,
                        "tag": "tag1",
                        "description": "description1",
                        "color": "blue",
                        "entity_possible": False,
                    }
                ],
                "schema_relations": [
                    {
                        "id": 1,
                        "tag": "tag1",
                        "description": "description1",
                    }
                ],
                "schema_constraints": [
                    {
                        "id": 1,
                        "is_directed": True,
                        "schema_relation": {
                            "id": 1,
                            "description": "relation_description",
                            "tag": "relation_tag",
                        },
                        "schema_mention_head": {
                            "id": 1,
                            "description": "mention_head_description",
                            "tag": "mention_head_tag",
                            "color": "mention_head_color",
                            "entity_possible": True,
                        },
                        "schema_mention_tail": {
                            "id": 2,
                            "description": "mention_tail_description",
                            "tag": "mention_tail_tag",
                            "color": "mention_tail_color",
                            "entity_possible": False,
                        },
                    }
                ],
            },
        )
