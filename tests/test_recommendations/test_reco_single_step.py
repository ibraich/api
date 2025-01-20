import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, BadRequest
from app.services.recommendation_service import RecommendationService
from app.routes.document_routes import DocumentRoutes, RecommendationRoutes, RecommendationManagementRoutes

class TestRecommendationRoutes(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.recommendation_service_mock = MagicMock(spec=RecommendationService)

    @patch('app.routes.document_routes.RecommendationService', return_value=MagicMock())
    def test_get_recommendations_success(self, mock_service):
        mock_service.return_value.get_recommendations_for_document.return_value = [{
            "mention_id": 1,
            "schema_id": 2,
            "recommendation": "Sample Recommendation"
        }]

        with self.app.test_request_context('/api/recommendations?document_id=1', method='GET'):
            response = RecommendationRoutes().get()

        self.assertEqual(response[1], 200)
        self.assertIn("Sample Recommendation", jsonify(response[0]).json[0]["recommendation"])

    @patch('app.routes.document_routes.RecommendationService', return_value=MagicMock())
    def test_get_recommendations_not_found(self, mock_service):
        mock_service.return_value.get_recommendations_for_document.side_effect = NotFound("No document edit found")

        with self.app.test_request_context('/api/recommendations?document_id=1', method='GET'):
            response = RecommendationRoutes().get()

        self.assertEqual(response[1], 404)
        self.assertIn("No document edit found", response[0]["error"])

    @patch('app.routes.document_routes.RecommendationService', return_value=MagicMock())
    def test_delete_recommendation_success(self, mock_service):
        mock_service.return_value.delete_recommendation_by_id.return_value = None

        with self.app.test_request_context('/api/recommendations/1', method='DELETE'):
            response = RecommendationManagementRoutes().delete(1)

        self.assertEqual(response[1], 200)
        self.assertIn("Recommendation deleted successfully", jsonify(response[0]).json["message"])

    @patch('app.routes.document_routes.RecommendationService', return_value=MagicMock())
    def test_delete_recommendation_not_found(self, mock_service):
        mock_service.return_value.delete_recommendation_by_id.side_effect = NotFound("Recommendation ID does not exist")

        with self.app.test_request_context('/api/recommendations/1', method='DELETE'):
            response = RecommendationManagementRoutes().delete(1)

        self.assertEqual(response[1], 404)
        self.assertIn("Recommendation ID does not exist", response[0]["error"])

if __name__ == '__main__':
    unittest.main()
