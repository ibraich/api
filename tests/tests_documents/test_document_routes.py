
import unittest
from unittest.mock import patch
from flask import Flask
from app.routes.document_routes import ns as document_ns
from flask_restx import Api

class TestDocumentRoutes(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)
        api.add_namespace(document_ns, path="/documents")
        self.client = app.test_client()

    @patch("app.services.document_service.DocumentService.accept_recommendation")
    def test_accept_recommendation(self, mock_accept_recommendation):
        # Arrange
        mock_accept_recommendation.return_value = {"id": 1, "status": "accepted"}

        # Act
        response = self.client.put(
            "/documents/recommendations/1", json={"action": "accept"}
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recommendation accepted successfully.", response.json["message"])

    @patch("app.services.document_service.DocumentService.reject_recommendation")
    def test_reject_recommendation(self, mock_reject_recommendation):
        # Arrange
        mock_reject_recommendation.return_value = {"status": "Recommendation rejected"}

        # Act
        response = self.client.put(
            "/documents/recommendations/1", json={"action": "reject"}
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recommendation rejected successfully.", response.json["message"])

if __name__ == "__main__":
    unittest.main()
