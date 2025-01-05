import unittest
from unittest.mock import MagicMock
from werkzeug.exceptions import NotFound, BadRequest
from app.services.document_service import DocumentService

class TestDocumentUpload(unittest.TestCase):
    def setUp(self):
        self.document_repository = MagicMock()
        self.user_service = MagicMock()
        self.project_service = MagicMock()
        self.service = DocumentService(
            document_repository=self.document_repository,
            user_service=self.user_service
        )
        self.service.__project_service = self.project_service

    def test_upload_document_success(self):
        self.project_service.get_project_by_id.return_value = MagicMock(team_id=1)
        self.user_service.is_user_in_team.return_value = True
        self.document_repository.create_document.return_value = MagicMock(id=1, name="test.txt")

        result = self.service.upload_document(1, 1, "test.txt", "This is the content.")
        self.assertEqual(result["name"], "test.txt")
        self.assertEqual(result["id"], 1)

    def test_upload_document_missing_content(self):
        with self.assertRaises(ValueError):
            self.service.upload_document(1, 1, "test.txt", " ")

