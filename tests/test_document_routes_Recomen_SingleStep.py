
import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from app.routes.document_routes import ns as document_ns


class TestDocumentRoutes(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)
        api.add_namespace(document_ns, path="/documents")
        self.client = app.test_client()

    @patch("app.services.document_service.DocumentService.regenerate_recommendations")
    def test_regenerate_recommendations(self, mock_regenerate):
        mock_regenerate.return_value = {"status": "success"}
        response = self.client.post("/documents/document-edit/1/regenerate/mentions")
        self.assertEqual(response.status_code, 200)
