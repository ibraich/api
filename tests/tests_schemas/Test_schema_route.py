import unittest
from app import app

class TestSchemaRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.schema_data = {
            "team_id": 1,
            "schema_mentions": [{"tag": "person"}],
            "schema_relations": [{"tag": "knows"}],
            "schema_constraints": [{"head": "person", "tail": "person", "relation": "knows"}],
        }

    def test_create_schema_success(self):
        response = self.app.post('/schemas', json=self.schema_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Schema created successfully.", response.json["message"])

    def test_create_schema_missing_fields(self):
        response = self.app.post('/schemas', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields.", response.json["error"])

    def test_create_schema_duplicate_mentions(self):
        # Duplicate mentions should be caught by the service
        self.schema_data["schema_mentions"].append({"tag": "person"})
        response = self.app.post('/schemas', json=self.schema_data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Duplicate tags in schema mentions.", response.json["error"])

    def test_create_schema_duplicate_constraints(self):
        # Duplicate constraints should be caught by the service
        self.schema_data["schema_constraints"].append(
            {"head": "person", "tail": "person", "relation": "knows"}
        )
        response = self.app.post('/schemas', json=self.schema_data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("Duplicate schema constraints.", response.json["error"])
