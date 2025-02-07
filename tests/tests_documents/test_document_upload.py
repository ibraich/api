import unittest
from collections import namedtuple
from unittest.mock import MagicMock
from app.services.document_service import DocumentService
from tests.test_routes import BaseTestCase


class TestDocumentUpload(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service = DocumentService(
            document_repository=self.document_repository,
            token_service=self.token_service,
            document_edit_service=self.document_edit_service,
        )

    def test_upload_document_missing_content(self):
        with self.assertRaises(ValueError):
            self.service.upload_document(1, "test.txt", " ", " ")
