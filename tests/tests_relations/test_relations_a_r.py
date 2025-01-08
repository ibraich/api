
import unittest
from flask import Flask
from app.routes.relation_routes import ns as relation_namespace

class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_accept_relation(self):
        # Simuliere eine POST-Anfrage für das Akzeptieren einer Relation
        response = self.client.post("/relations/1/accept", headers={"User-ID": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("relation_id", response.json)

    def test_delete_relation(self):
        # Simuliere eine POST-Anfrage für das Ablehnen einer Relation
        response = self.client.post("/relations/1/delete", headers={"User-ID": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
