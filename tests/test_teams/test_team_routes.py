import unittest
from flask import Flask, jsonify
from flask.testing import FlaskClient
from unittest.mock import MagicMock, patch
from app.routes.team_routes import ns
from app.services.team_service import TeamService
from werkzeug.exceptions import NotFound, BadRequest


class TestTeamRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(ns)
        self.client: FlaskClient = self.app.test_client()

        self.mock_team_service = MagicMock(spec=TeamService)

    @patch("app.services.team_service.team_service", new_callable=MagicMock)
    def test_update_team_name_success(self, mock_team_service):
        mock_team_service.update_team_name.return_value = None

        response = self.client.put(
            "/teams/1",
            json={"name": "New Team Name"},
            headers={"Authorization": "Bearer test_token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Team updated successfully."})
        mock_team_service.update_team_name.assert_called_once_with(1, "New Team Name")

    @patch("app.services.team_service.team_service", new_callable=MagicMock)
    def test_update_team_name_not_found(self, mock_team_service):
        mock_team_service.update_team_name.side_effect = NotFound("Team not found.")

        response = self.client.put(
            "/teams/1",
            json={"name": "New Team Name"},
            headers={"Authorization": "Bearer test_token"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Team not found."})

    @patch("app.services.team_service.team_service", new_callable=MagicMock)
    def test_update_team_name_bad_request(self, mock_team_service):
        mock_team_service.update_team_name.side_effect = BadRequest("Invalid input.")

        response = self.client.put(
            "/teams/1",
            json={"name": ""},
            headers={"Authorization": "Bearer test_token"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid input."})
