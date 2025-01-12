
import unittest
from unittest.mock import patch
from flask import Flask, jsonify
from app.routes.api_routes import review_recommendation

class TestRecommendationAccept(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

    @patch('app.services.document_recommendation_service.DocumentRecommendationService.accept_recommendation')
    def test_accept_recommendation_success(self, mock_accept):
        mock_accept.return_value = {"status": "accepted", "document_edit_id": 123}
        with self.app.test_request_context(json={"action": "accept"}):
            response = review_recommendation(1)
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            self.assertEqual(response.json["result"]["status"], "accepted")

class TestRecommendationReject(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

    @patch('app.services.document_recommendation_service.DocumentRecommendationService.reject_recommendation')
    def test_reject_recommendation_success(self, mock_reject):
        mock_reject.return_value = {"status": "rejected"}
        with self.app.test_request_context(json={"action": "reject"}):
            response = review_recommendation(1)
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            self.assertEqual(response.json["result"]["status"], "rejected")

class TestRecommendationInvalidAction(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

    def test_invalid_action(self):
        with self.app.test_request_context(json={"action": "invalid_action"}):
            response = review_recommendation(1)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)

if __name__ == '__main__':
    unittest.main()
