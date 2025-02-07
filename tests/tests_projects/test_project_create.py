import unittest
from collections import namedtuple
from werkzeug.exceptions import BadRequest
from app.models import Project
from tests.test_routes import ProjectBaseTestCase


class TestProjectCreateResource(ProjectBaseTestCase):

    def setUp(self):
        super().setUp()

    def test_create_project_success(self):
        self.project_repository.get_project_by_name.return_value = None

        self.schema_service.fix_schema.return_value = None
        self.project_repository.create_project.return_value = Project(
            id=7, name="Project7"
        )
        self.project_repository.get_project_by_id.return_value = project_response(
            7, "Project7", 1, 2, 3, "Schema", "Team2"
        )
        response = self.service.create_project(1, 2, 3, "Project7")

        # Assertions
        self.assertEqual(response["id"], 7)
        self.assertEqual(response["team"]["name"], "Team2")

        self.project_repository.get_project_by_name.assert_called_with("Project7")

        self.schema_service.fix_schema.assert_called()
        self.project_repository.create_project.assert_called()

    def test_create_project_name_exists(self):
        self.project_repository.get_project_by_name.side_effect = BadRequest()

        with self.assertRaises(BadRequest):
            self.service.create_project(1, 2, 3, "Project7")


project_response = namedtuple(
    "ProjectResponse",
    ["id", "name", "creator_id", "team_id", "schema_id", "schema_name", "team_name"],
)

if __name__ == "__main__":
    unittest.main()
