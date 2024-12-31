from collections import namedtuple

from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService, project_service
from tests.test_routes import BaseTestCase
from unittest.mock import patch
from app.services.user_service import UserService


class ProjectsFetchByUserTestCase(BaseTestCase):
    service: ProjectService

    def setUp(self):
        super().setUp()
        self.service = project_service

    @patch.object(ProjectService, "get_projects_by_user")
    def test_get_teams_by_user_endpoint_valid(
        self,
        get_projects_by_user_mock,
    ):

        get_projects_by_user_mock.return_value = {
            "projects": [
                {
                    "id": 1,
                    "name": "Project1",
                    "creator_id": 1,
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_id": 1,
                },
                {
                    "id": 2,
                    "name": "Project2",
                    "creator_id": 2,
                    "team_id": 3,
                    "team_name": "Team3",
                    "schema_id": 2,
                },
            ]
        }

        response = self.client.get(
            "/api/projects/",
            headers={"Content-Type": "application/json"},
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.json,
            {
                "projects": [
                    {
                        "id": 1,
                        "name": "Project1",
                        "creator_id": 1,
                        "team_id": 1,
                        "team_name": "Team1",
                        "schema_id": 1,
                    },
                    {
                        "id": 2,
                        "name": "Project2",
                        "creator_id": 2,
                        "team_id": 3,
                        "team_name": "Team3",
                        "schema_id": 2,
                    },
                ]
            },
        )

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(ProjectRepository, "get_projects_by_user")
    def test_get_projects_by_user_no_projects(self, get_projects_mock, get_user_mock):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1
        get_projects_mock.return_value = None

        response = self.client.get("/api/projects/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual({"projects": []}, response.json)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(ProjectRepository, "get_projects_by_user")
    def test_get_projects_by_user_service_valid(self, get_projects_mock, get_user_mock):
        get_user_mock.return_value = 1

        project_return = namedtuple(
            "Team",
            ["id", "name", "creator_id", "team_id", "team_name", "schema_id"],
        )
        get_projects_mock.return_value = [
            project_return(1, "Teamname", 6, 2, "Team2", 3)
        ]

        response = self.client.get("/api/projects/")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "projects": [
                    {
                        "id": 1,
                        "name": "Teamname",
                        "creator_id": 6,
                        "team_id": 2,
                        "team_name": "Team2",
                        "schema_id": 3,
                    }
                ]
            },
            response.json,
        )
