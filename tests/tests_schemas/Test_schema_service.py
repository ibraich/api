import unittest
from unittest.mock import MagicMock
from schema_service import SchemaService
from werkzeug.exceptions import Conflict

class TestSchemaService(unittest.TestCase):
    def setUp(self):
        self.schema_service = SchemaService()
        self.schema_service.schema_repo = MagicMock()  # Mock repository
        self.schema_data = {
            "team_id": 1,
            "mentions": [{"tag": "person"}],
            "relations": [{"tag": "knows"}],
            "constraints": [{"head": "person", "tail": "person", "relation": "knows"}],
        }

    def test_create_schema_success(self):
        # Mock repository methods
        self.schema_service.schema_repo.create_schema.return_value = 1
        self.schema_service.schema_repo.add_mentions.return_value = None
        self.schema_service.schema_repo.add_relations.return_value = None
        self.schema_service.schema_repo.add_constraints.return_value = None

        self.schema_service.create_schema(
            self.schema_data["team_id"],
            self.schema_data["mentions"],
            self.schema_data["relations"],
            self.schema_data["constraints"]
        )

        # Check that repository methods were called
        self.schema_service.schema_repo.create_schema.assert_called_once_with(1)
        self.schema_service.schema_repo.add_mentions.assert_called_once()
        self.schema_service.schema_repo.add_relations.assert_called_once()
        self.schema_service.schema_repo.add_constraints.assert_called_once()

    def test_create_schema_duplicate_mentions(self):
        self.schema_data["mentions"].append({"tag": "person"})
        with self.assertRaises(Conflict) as context:
            self.schema_service.create_schema(
                self.schema_data["team_id"],
                self.schema_data["mentions"],
                self.schema_data["relations"],
                self.schema_data["constraints"]
            )
        self.assertIn("Duplicate tags in schema mentions.", str(context.exception))

    def test_create_schema_duplicate_constraints(self):
        self.schema_data["constraints"].append(
            {"head": "person", "tail": "person", "relation": "knows"}
        )
        with self.assertRaises(Conflict) as context:
            self.schema_service.create_schema(
                self.schema_data["team_id"],
                self.schema_data["mentions"],
                self.schema_data["relations"],
                self.schema_data["constraints"]
            )
        self.assertIn("Duplicate schema constraints.", str(context.exception))
