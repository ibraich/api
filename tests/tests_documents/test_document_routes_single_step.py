
import unittest
from unittest.mock import patch
from app import app

class TestDocumentRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("app.services.document_service.document_service.regenerate_recommendations")
    @patch("app.services.user_service.user_service.get_logged_in_user_id")
    def test_regenerate_recommendations_mentions_success(self, mock_get_user, mock_service):
        mock_get_user.return_value = 1
        mock_service.return_value = {"message": "Mentions recommendations regenerated successfully."}
        response = self.app.post(
            "/documents/1/regenerate-recommendations?step=mentions",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Mentions recommendations regenerated successfully.", response.json["message"])

    @patch("app.services.document_service.document_service.regenerate_recommendations")
    @patch("app.services.user_service.user_service.get_logged_in_user_id")
    def test_invalid_step(self, mock_get_user, mock_service):
        mock_get_user.return_value = 1
        response = self.app.post(
            "/documents/1/regenerate-recommendations?step=invalid_step",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid step provided.", response.json["error"])

    @patch("app.services.document_service.document_service.regenerate_recommendations")
    @patch("app.services.user_service.user_service.get_logged_in_user_id")
    def test_unauthorized_access(self, mock_get_user, mock_service):
        mock_get_user.return_value = None
        response = self.app.post(
            "/documents/1/regenerate-recommendations?step=mentions",
        )
        self.assertEqual(response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
