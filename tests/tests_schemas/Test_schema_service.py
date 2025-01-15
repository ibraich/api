import unittest
from unittest.mock import MagicMock
from werkzeug.exceptions import BadRequest
from app.services.schema_service import SchemaService
from app.repositories.schema_repository import SchemaRepository
from app.services.user_service import UserService

class TestSchemaService(unittest.TestCase):
    def setUp(self):
        # Mock the repository and user service
        self.schema_repository = MagicMock(spec=SchemaRepository)
        self.user_service = MagicMock(spec=UserService)

        # Create the service instance
        self.service = SchemaService(self.schema_repository, self.user_service)

    def test_create_schema_success(self):
        # Mock data
        team_id = 1
        user_id = 2
        name = "Test Schema"
        modelling_language_id = 1
        mentions = [{"tag": "mention1"}, {"tag": "mention2"}]
        relations = [{"tag": "relation1"}, {"tag": "relation2"}]
        constraints = [{"head": "mention1", "tail": "mention2", "relation": "relation1"}]

        # Mock user validation
        self.user_service.check_user_in_team.return_value = True

        # Mock schema creation
        self.schema_repository.create_schema.return_value = 123
        self.schema_repository.get_schema_by_id.return_value = {"id": 123, "name": name}
        self.schema_repository.get_schema_mentions.return_value = mentions
        self.schema_repository.get_schema_relations.return_value = relations
        self.schema_repository.get_schema_constraints.return_value = constraints

        # Call the service
        result = self.service.create_schema(team_id, user_id, name, modelling_language_id, mentions, relations, constraints)

        # Assertions
        self.assertEqual(result["schema"]["id"], 123)
        self.assertEqual(result["schema"]["name"], name)
        self.assertEqual(result["mentions"], mentions)
        self.assertEqual(result["relations"], relations)
        self.assertEqual(result["constraints"], constraints)

    def test_create_schema_user_not_in_team(self):
        # Mock data
        team_id = 1
        user_id = 2
        name = "Test Schema"
        modelling_language_id = 1
        mentions = [{"tag": "mention1"}, {"tag": "mention2"}]
        relations = [{"tag": "relation1"}, {"tag": "relation2"}]
        constraints = [{"head": "mention1", "tail": "mention2", "relation": "relation1"}]

        # Mock user validation failure
        self.user_service.check_user_in_team.return_value = False

        # Call the service and expect an exception
        with self.assertRaises(BadRequest):
            self.service.create_schema(team_id, user_id, name, modelling_language_id, mentions, relations, constraints)

    def test_create_schema_duplicate_tags(self):
        # Mock data with duplicate tags
        team_id = 1
        user_id = 2
        name = "Test Schema"
        modelling_language_id = 1
        mentions = [{"tag": "mention1"}, {"tag": "mention1"}]
        relations = [{"tag": "relation1"}, {"tag": "relation2"}]
        constraints = [{"head": "mention1", "tail": "mention2", "relation": "relation1"}]

        # Mock user validation
        self.user_service.check_user_in_team.return_value = True

        # Call the service and expect an exception
        with self.assertRaises(BadRequest):
            self.service.create_schema(team_id, user_id, name, modelling_language_id, mentions, relations, constraints)
