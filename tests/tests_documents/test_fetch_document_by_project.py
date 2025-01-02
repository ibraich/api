from tests.test_routes import BaseTestCase
from unittest.mock import patch
from app.services.document_service import DocumentService, document_service


class DocumentsFetchByUserTestCase(BaseTestCase):
    service: DocumentService

    def setUp(self):
        super().setUp()
        self.service = document_service

    @patch.object(DocumentService, "get_documents_by_project")
    def test_fetch_documents_by_project_endpoint(self, fetch_documents_by_project_mock):

        fetch_documents_by_project_mock.return_value = [
            {
                "id": 1,
                "content": "Doc Text1",
                "name": "Doc1",
                "team_id": 1,
                "team_name": "Team1",
                "schema_id": 1,
                "project_id": 1,
                "project_name": "Project1",
                "document_edit_id": 1,
                "document_edit_state": "MENTIONS",
            },
            {
                "id": 2,
                "content": "Doc Text2",
                "name": "Doc2",
                "team_id": 1,
                "team_name": "Team1",
                "schema_id": 1,
                "project_id": 1,
                "project_name": "Project1",
                "document_edit_id": None,
                "document_edit_state": None,
            },
        ]

        response = self.client.get(
            "/api/documents/project/1",
            headers={"Content-Type": "application/json"},
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.json,
            [
                {
                    "id": 1,
                    "content": "Doc Text1",
                    "name": "Doc1",
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_id": 1,
                    "project_id": 1,
                    "project_name": "Project1",
                    "document_edit_id": 1,
                    "document_edit_state": "MENTIONS",
                },
                {
                    "id": 2,
                    "content": "Doc Text2",
                    "name": "Doc2",
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_id": 1,
                    "project_id": 1,
                    "project_name": "Project1",
                    "document_edit_id": None,
                    "document_edit_state": None,
                },
            ],
        )

    @patch.object(DocumentService, "get_documents_by_user")
    def test_fetch_documents_by_project_service_valid(
        self,
        get_documents_by_user_mock,
    ):

        get_documents_by_user_mock.return_value = [
            {
                "id": 1,
                "content": "Doc Text1",
                "name": "Doc1",
                "team_id": 1,
                "team_name": "Team1",
                "schema_id": 1,
                "project_id": 1,
                "project_name": "Project1",
                "document_edit_id": 1,
                "document_edit_state": "MENTIONS",
            },
            {
                "id": 4,
                "content": "Doc Text4",
                "name": "Doc4",
                "team_id": 3,
                "team_name": "Team3",
                "schema_id": 2,
                "project_id": 2,
                "project_name": "Project2",
                "document_edit_id": None,
                "document_edit_state": None,
            },
        ]

        response = self.client.get(
            "/api/documents/project/1",
            headers={"Content-Type": "application/json"},
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.json,
            [
                {
                    "id": 1,
                    "content": "Doc Text1",
                    "name": "Doc1",
                    "team_id": 1,
                    "team_name": "Team1",
                    "schema_id": 1,
                    "project_id": 1,
                    "project_name": "Project1",
                    "document_edit_id": 1,
                    "document_edit_state": "MENTIONS",
                }
            ],
        )
