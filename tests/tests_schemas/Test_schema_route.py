import unittest
from unittest.mock import patch
from app import app

class TestSchemaRoutes(unittest.TestCase):
    @patch("app.services.schema_service.SchemaService.create_schema")
    @patch("app.services.user_service.UserService.get_logged_in_user_id")
    def test_create_schema_success(self, mock_get_user_id, mock_create_schema):
        mock_get_user_id.return_value = 1
        mock_create_schema.return_value = 123

        payload = {
            "team_id": 1,
            "name": "Test Schema",
            "modelling_language_id": 1,
            "mentions": [{"tag": "mention1"}, {"tag": "mention2"}],
            "relations": [{"tag": "relation1"}, {"tag": "relation2"}],
            "constraints": [{"head": "mention1", "tail": "mention2", "relation": "relation1"}],
        }

        client = app.test_client()
        response = client.post("/schemas/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Schema created successfully", response.get_json()["message"])