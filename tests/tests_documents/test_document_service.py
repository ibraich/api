
import unittest
from unittest.mock import MagicMock
from app.services.document_service import DocumentService_Reccomendation_a_r
from app.repositories.document_repository import Recommendation_a_r
from werkzeug.exceptions import NotFound

class TestDocumentService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=Recommendation_a_r)
        self.service = DocumentService_Reccomendation_a_r(self.mock_repository, MagicMock())

    def test_accept_recommendation(self):
        # Arrange
        mock_recommendation = MagicMock(is_entity=False)
        self.mock_repository.get_recommendation_by_id.return_value = mock_recommendation
        self.mock_repository.copy_recommendation_to_edit.return_value = "mock_edit"

        # Act
        result = self.service.accept_recommendation(1)

        # Assert
        self.mock_repository.get_recommendation_by_id.assert_called_once_with(1)
        self.mock_repository.copy_recommendation_to_edit.assert_called_once_with(1)
        self.assertEqual(result, "mock_edit")

    def test_accept_recommendation_not_found(self):
        # Arrange
        self.mock_repository.get_recommendation_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            self.service.accept_recommendation(1)

    def test_reject_recommendation(self):
        # Arrange
        mock_recommendation = MagicMock()
        self.mock_repository.get_recommendation_by_id.return_value = mock_recommendation

        # Act
        result = self.service.reject_recommendation(1)

        # Assert
        self.mock_repository.get_recommendation_by_id.assert_called_once_with(1)
        self.mock_repository.mark_recommendation_as_not_shown.assert_called_once_with(1)
        self.assertEqual(result["status"], "Recommendation rejected")

if __name__ == "__main__":
    unittest.main()
