
import unittest
from unittest.mock import MagicMock
from app.services.document_service import DocumentService_Recomen_SingleStep


class TestDocumentService_Recomen_SingleStep(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock()
        self.service = DocumentService_Recomen_SingleStep(self.mock_repository)

    def test_regenerate_recommendations(self):
        self.mock_repository.get_user_id.return_value = 1
        self.mock_repository.delete_existing_recommendations = MagicMock()
        self.mock_repository.store_new_recommendations = MagicMock()
        self.service.query_recommendation_system = MagicMock(
            return_value=[{"content": "Mention 1", "type": "mention"}]
        )

        response = self.service.regenerate_recommendations(1, "mentions")
        self.assertEqual(response["status"], "success")
        self.assertTrue("recommendations" in response)
