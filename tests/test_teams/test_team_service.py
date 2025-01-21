import unittest
from unittest.mock import MagicMock
from werkzeug.exceptions import BadRequest, NotFound
from app.services.team_service import TeamService
from app.repositories.team_repository import TeamRepository
from werkzeug.exceptions import NotFound, BadRequest


class TestTeamService(unittest.TestCase):
    def setUp(self):
        self.mock_team_repository = MagicMock(spec=TeamRepository)
        self.team_service = TeamService(self.mock_team_repository)

    def test_update_team_name_success(self):
        self.mock_team_repository.update_team_name.return_value = True

        self.team_service.update_team_name(1, "New Team Name")

        self.mock_team_repository.update_team_name.assert_called_once_with(
            1, "New Team Name"
        )

    def test_update_team_name_not_found(self):
        self.mock_team_repository.update_team_name.return_value = False

        with self.assertRaises(NotFound):
            self.team_service.update_team_name(1, "New Team Name")

    def test_update_team_name_bad_request(self):
        with self.assertRaises(BadRequest):
            self.team_service.update_team_name(1, "")

        with self.assertRaises(BadRequest):
            self.team_service.update_team_name(1, "   ")
