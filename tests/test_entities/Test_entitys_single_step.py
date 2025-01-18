import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.entity_routes import ns as entity_namespace

import os

RECOMMENDATION_SYSTEM_URL = os.getenv("RECOMMENDATION_SYSTEM_URL", "http://localhost:8080/pipeline/docs")

app = Flask(__name__)
app.register_blueprint(entity_namespace)

class TestEntityResource(unittest.TestCase):

    @patch("requests.post")
    def test_post_entity_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"result": "success"})

        with app.test_client() as client:
            response = client.post(
                "/entities/",
                json={"document_id": 1},
                query_string={"model_type": "llm", "model": "gpt-4o-mini", "temperature": "none"}
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn("result", response.json)

    @patch("requests.post")
    def test_post_entity_invalid_payload(self, mock_post):
        with app.test_client() as client:
            response = client.post(
                "/entities/",
                query_string={"model_type": "llm", "model": "gpt-4o-mini", "temperature": "none"}
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)

    @patch("requests.post")
    def test_post_entity_external_error(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500, text="Internal error")

        with app.test_client() as client:
            response = client.post(
                "/entities/",
                json={"document_id": 1},
                query_string={"model_type": "llm", "model": "gpt-4o-mini", "temperature": "none"}
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)

    @patch("requests.get")
    def test_get_entity_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"entity": "Sample Entity"})

        with app.test_client() as client:
            response = client.get("/entities/1")

            self.assertEqual(response.status_code, 200)
            self.assertIn("entity", response.json)

    @patch("requests.get")
    def test_get_entity_not_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)

        with app.test_client() as client:
            response = client.get("/entities/1")

            self.assertEqual(response.status_code, 404)
            self.assertIn("error", response.json)

    @patch("requests.delete")
    def test_delete_entity_success(self, mock_delete):
        mock_delete.return_value = MagicMock(status_code=200)

        with app.test_client() as client:
            response = client.delete("/entities/1")

            self.assertEqual(response.status_code, 200)
            self.assertIn("message", response.json)

    @patch("requests.delete")
    def test_delete_entity_not_found(self, mock_delete):
        mock_delete.return_value = MagicMock(status_code=404)

        with app.test_client() as client:
            response = client.delete("/entities/1")

            self.assertEqual(response.status_code, 404)
            self.assertIn("error", response.json)

if __name__ == "__main__":
    unittest.main()


