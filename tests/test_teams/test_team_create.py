from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound

from app.repositories.team_repository import TeamRepository
from tests.test_routes import BaseTestCase
from unittest.mock import patch, MagicMock
import json
from app.services.team_service import TeamService, team_service
from app.services.user_service import UserService
from app.services.schema_service import SchemaService
from app.db import db


class TeamCreateTestCases(BaseTestCase):
    service: TeamService

    def setUp(self):
        super().setUp()
        self.service = team_service

    @patch.object(TeamService, "create_team")
    def test_create_team_endpoint(self, create_team_mock):
        payload = json.dumps({"name": "team-Name"})

        create_team_mock.return_value = ""
        response = self.client.post(
            "/api/teams/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        self.assertEqual(200, response.status_code)

    @patch.object(TeamService, "create_team")
    def test_create_team_service_wrong_param(self, create_team_mock):
        payload = json.dumps({"id": 7})

        create_team_mock.return_value = ""
        response = self.client.post(
            "/api/teams/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        self.assertEqual(400, response.status_code)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(TeamRepository, "create_team")
    def test_create_team_service_name_already_exists(
        self, create_team_mock, check_auth_mock
    ):
        payload = json.dumps({"name": "team-Name"})

        check_auth_mock.return_value = 1
        create_team_mock.side_effect = IntegrityError("Mock", "Mock", MagicMock())

        response = self.client.post(
            "/api/teams/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json.get("message"), "Teamname already exists")

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(db.session, "add")
    @patch.object(db.session, "commit")
    def test_create_team_service_valid(
        self,
        db_mock_commit,
        db_mock_add,
        check_auth_mock,
    ):
        payload = json.dumps({"name": "team-Name"})

        check_auth_mock.return_value = 1

        response = self.client.post(
            "/api/teams/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )

        db_mock_add.assert_called_once()
        db_mock_commit.assert_called_once()
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json.get("name"), "team-Name")
