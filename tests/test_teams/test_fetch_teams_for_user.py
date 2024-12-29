from collections import namedtuple

from app.repositories.team_repository import TeamRepository
from tests.test_routes import BaseTestCase
from unittest.mock import patch
from app.services.team_service import TeamService, team_service
from app.services.user_service import UserService


class TeamsFetchByUserTestCase(BaseTestCase):
    service: TeamService

    def setUp(self):
        super().setUp()
        self.service = team_service

    @patch.object(TeamService, "get_teams_by_user")
    def test_get_teams_by_user_endpoint_valid(
        self,
        get_teams_by_user_mock,
    ):

        get_teams_by_user_mock.return_value = {
            "teams": [
                {
                    "id": 1,
                    "name": "Team1",
                    "creator_id": 1,
                    "members": [
                        {"id": 1, "username": "User1", "email": "mail1@com"},
                        {"id": 3, "username": "User3", "email": "mail3@com"},
                    ],
                }
            ]
        }

        response = self.client.get(
            "/api/teams/",
            headers={"Content-Type": "application/json"},
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.json,
            {
                "teams": [
                    {
                        "id": 1,
                        "name": "Team1",
                        "creator_id": 1,
                        "members": [
                            {"id": 1, "username": "User1", "email": "mail1@com"},
                            {"id": 3, "username": "User3", "email": "mail3@com"},
                        ],
                    }
                ]
            },
        )

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(TeamRepository, "get_teams_by_user")
    def test_get_teams_by_user_no_teams(self, get_teams_mock, get_user_mock):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1
        get_teams_mock.return_value = None

        response = self.client.get("/api/teams/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual({"teams": []}, response.json)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(TeamRepository, "get_teams_by_user")
    @patch.object(TeamService, "_TeamService__get_team_members_by_team_id")
    def test_get_teams_by_user_service_valid(
        self, get_team_member_mock, get_teams_mock, get_user_mock
    ):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1

        team_return = namedtuple(
            "Team",
            ["id", "name", "creator_id"],
        )
        get_teams_mock.return_value = [team_return(1, "Teamname", 6)]

        get_team_member_mock.return_value = [
            {
                "id": 1,
                "username": "Username1",
                "email": "Email2",
            },
            {
                "id": 2,
                "username": "Username1",
                "email": "Email2",
            },
        ]

        response = self.client.get("/api/teams/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "teams": [
                    {
                        "id": 1,
                        "name": "Teamname",
                        "creator_id": 6,
                        "members": [
                            {
                                "id": 1,
                                "username": "Username1",
                                "email": "Email2",
                            },
                            {
                                "id": 2,
                                "username": "Username1",
                                "email": "Email2",
                            },
                        ],
                    }
                ]
            },
            response.json,
        )
