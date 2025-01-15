import unittest
from unittest.mock import patch
from flask import Flask

class MentionRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    @patch("app.routes.mention_service.accept_recommendation")
    def test_accept_mention_route(self, mock_accept):
        mock_accept.return_value = {"id": 1, "content": "Test mention", "is_shown_recommendation": False}
        response = self.client.post("/mention/1/accept", json={"content": "Test mention"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test mention", response.get_json()["content"])

    @patch("app.routes.mention_service.reject_recommendation")
    def test_reject_mention_route(self, mock_reject):
        mock_reject.return_value = {"id": 1, "content": "Test mention", "is_shown_recommendation": False}
        response = self.client.post("/mention/1/reject", json={"content": "Test mention"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test mention", response.get_json()["content"])
