import unittest
from unittest.mock import patch

from werkzeug.exceptions import BadRequest

from app.models import (
    Schema,
    DocumentEdit,
    DocumentRecommendation,
)
from app.services.document_edit_service import DocumentEditService

from tests.test_routes import DocumentEditBaseTestCase


class TestDocumentEditCreateResource(DocumentEditBaseTestCase):

    def setUp(self):
        super().setUp()

    @patch.object(
        DocumentEditService, "_DocumentEditService__get_document_edit_by_document"
    )
    @patch.object(
        DocumentEditService,
        "_DocumentEditService__get_document_edit_with_document_by_id",
    )
    def test_create_document_edit_success(self, get_edit_doc_mock, get_edit_mock):
        get_edit_mock.return_value = None

        # Get schema of document
        self.schema_service.get_schema_by_document.return_value = Schema(id=1)

        # Verify models are valid for given schema and steps
        self.schema_service.check_models_in_schema.return_value = None

        # Create document edit
        document_edit = DocumentEdit(id=2)
        document_edit.content = "Content"
        self.document_edit_repository.create_document_edit.return_value = document_edit

        get_edit_doc_mock.return_value = document_edit

        # Create document recommendation for document edit
        document_recommendation = DocumentRecommendation(id=8)
        self.document_recommendation_service.create_document_recommendation.return_value = (
            document_recommendation
        )

        # Store model settings
        self.document_edit_repository.store_model_settings.return_value = None

        self.document_recommendation_service.get_mention_recommendation.return_value = (
            None
        )

        self.mention_service.create_recommended_mention.return_value = None

        response = self.service.create_document_edit(1, 2, 3, 4, 5)

        self.assertEqual(2, response["id"])

        # Assert all functions are called
        self.schema_service.get_schema_by_document.assert_called()
        self.schema_service.check_models_in_schema.assert_called()
        self.document_edit_repository.create_document_edit.assert_called()
        self.document_recommendation_service.create_document_recommendation.assert_called()
        self.document_edit_repository.store_model_settings.assert_called()
        self.document_recommendation_service.get_mention_recommendation.assert_called()
        self.mention_service.create_recommended_mention.assert_called()

    @patch.object(
        DocumentEditService, "_DocumentEditService__get_document_edit_by_document"
    )
    def test_create_document_edit_invalid_model(self, get_edit_mock):
        get_edit_mock.return_value = None

        # Get schema of document
        self.schema_service.get_schema_by_document.return_value = Schema(id=1)

        # Verify models are valid for given schema and steps
        self.schema_service.check_models_in_schema.side_effect = BadRequest()

        with self.assertRaises(BadRequest):
            self.service.create_document_edit(1, 2, 3, 4, 5)


if __name__ == "__main__":
    unittest.main()
