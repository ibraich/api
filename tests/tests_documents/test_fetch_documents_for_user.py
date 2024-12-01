from collections import namedtuple

from app.repositories.document_repository import DocumentRepository
from app.services.project_service import ProjectService
from tests.test_routes import BaseTestCase
from unittest.mock import patch
import json
from app.services.document_service import DocumentService, document_service
from app.services.user_service import UserService
from app.services.schema_service import SchemaService
from app.db import db


class DocumentsFetchByUserTestCase(BaseTestCase):
    service: DocumentService

    def setUp(self):
        super().setUp()
        self.service = document_service

    @patch.object(DocumentService, "get_documents_by_user")
    def test_get_documents_by_user_bad_request(self, get_documents_mock):
        # Mock the service to simulate no service call (validation fails early)
        get_documents_mock.return_value = None

        # Sending POST request with invalid user ID (non-integer)
        payload = json.dumps({"user_id": "abcde"})
        response = self.client.post(
            "/api/documents/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )

        # Assert the response is 400 for bad input
        self.assertEqual(400, response.status_code)
        response_data = response.json
        self.assertEqual(
            response.json.get("message"),
            "400 Bad Request: User ID must be a valid integer.",
        )

    @patch.object(UserService, "check_authentication")
    @patch.object(DocumentService, "_DocumentService__get_documents_by_project_list")
    @patch.object(ProjectService, "get_projects_by_user")
    @patch.object(DocumentRepository, "get_document_edit_by_user_and_document")
    def test_get_documents_by_user_valid(
        self,
        get_document_edit_by_user_and_document_mock,
        get_projects_by_user_mock,
        get_documents_by_project_list_mock,
        check_authentication_mock,
    ):
        # Mock the service to simulate no service call (validation fails early)
        check_authentication_mock.return_value = "", 200
        get_projects_by_user_mock.return_value = None
        get_documents_by_project_list_mock.return_value = [
            {
                "content": "dummy doc text2",
                "id": 2,
                "name": "dummy doc2",
                "project_id": 12,
                "project_name": "Project-Name2",
                "type": "NEW",
            },
            {
                "content": "dummy doc text2",
                "id": 3,
                "name": "dummy doc2",
                "project_id": 12,
                "project_name": "Project-Name2",
                "type": "FINISHED",
            },
        ]
        mocked_return = namedtuple("tuple", ["id", "type"])
        get_document_edit_by_user_and_document_mock.return_value = mocked_return(
            3,
            "MENTIONS",
        )
        # Sending POST request with invalid user ID (non-integer)
        payload = json.dumps({"user_id": 1})

        response = self.client.post(
            "/api/documents/",
            headers={"Content-Type": "application/json"},
            data=payload,
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        response_data = response.json
        self.assertEqual(
            response.json,
            [
                {
                    "content": "dummy doc text2",
                    "document_edit_id": 3,
                    "document_edit_type": "MENTIONS",
                    "id": 2,
                    "name": "dummy doc2",
                    "project_id": 12,
                    "project_name": "Project-Name2",
                    "type": "NEW",
                },
                {
                    "content": "dummy doc text2",
                    "document_edit_id": 3,
                    "document_edit_type": "MENTIONS",
                    "id": 3,
                    "name": "dummy doc2",
                    "project_id": 12,
                    "project_name": "Project-Name2",
                    "type": "FINISHED",
                },
            ],
        )
