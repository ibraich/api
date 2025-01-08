
import unittest
from flask import Flask
from app.routes.mention_routes import ns as mention_namespace

class TestMentionRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_accept_mention(self):
        # Simuliere eine POST-Anfrage für das Akzeptieren einer Mention
        response = self.client.post("/mentions/1/accept", headers={"User-ID": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("mention_id", response.json)

    def test_delete_mention(self):
        # Simuliere eine POST-Anfrage für das Ablehnen einer Mention
        response = self.client.post("/mentions/1/delete", headers={"User-ID": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
