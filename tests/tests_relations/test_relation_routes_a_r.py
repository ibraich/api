import unittest
from unittest.mock import patch
from flask import Flask

class RelationRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    @patch("app.routes.relation_service.accept_recommendation")
    def test_accept_relation_route(self, mock_accept):
        mock_accept.return_value = {"id": 1, "content": "Test relation", "is_shown_recommendation": False}
        response = self.client.post("/relation/1/accept", json={"content": "Test relation"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test relation", response.get_json()["content"])

    @patch("app.routes.relation_service.reject_recommendation")
    def test_reject_relation_route(self, mock_reject):
        mock_reject.return_value = {"id": 1, "content": "Test relation", "is_shown_recommendation": False}
        response = self.client.post("/relation/1/reject", json={"content": "Test relation"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test relation", response.get_json()["content"])
