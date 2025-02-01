import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_restx import Api
from werkzeug.exceptions import NotFound, BadRequest

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.team_service import TeamService
from app.repositories.team_repository import TeamRepository
from app.routes.team_routes import ns as team_ns

class TestTeamServiceAndRoutes(unittest.TestCase):
    def setUp(self):
        # Set up Flask application and RESTx API
        app = Flask(__name__)
        api = Api(app)
        api.add_namespace(team_ns)
        self.app = app.test_client()

        # Mock repository
        self.mock_repo = MagicMock()
        self.team_service = TeamService(self.mock_repo, MagicMock(), MagicMock())

        # Patch TeamService to use the mocked service
        self.service_patch = patch('app.routes.team_routes.TeamService', return_value=self.team_service).start()

    def tearDown(self):
        patch.stopall()

    def test_delete_team_success(self):
        # Mock repository behavior
        self.mock_repo.soft_delete_team.return_value = True
        self.team_service.project_service.get_project_ids_by_team_id.return_value = [101, 102]
        self.team_service.project_service.soft_delete_project.return_value = None
        self.team_service.document_service.bulk_soft_delete_documents_by_project_id.return_value = None

        # Call DELETE endpoint
        response = self.app.delete('/teams', query_string={"team_id": 1})

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Team and all related records set to inactive successfully."})
        self.mock_repo.soft_delete_team.assert_called_once_with(1)

    def test_delete_team_not_found(self):
        # Mock repository to return False (team not found)
        self.mock_repo.soft_delete_team.return_value = False

        # Call DELETE endpoint
        response = self.app.delete('/teams', query_string={"team_id": 1})

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Team not found or already inactive."})

    def test_delete_team_invalid_id(self):
        # Call DELETE endpoint without a valid `team_id`
        response = self.app.delete('/teams', query_string={"team_id": -1})

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid team ID. Must be a positive integer."})

    def test_delete_team_missing_id(self):
        # Call DELETE endpoint without `team_id`
        response = self.app.delete('/teams')

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing team_id parameter"})
