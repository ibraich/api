import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from app.routes.mention_routes import MentionAcceptResource, MentionRejectResource

# Flask-App und API für Tests erstellen
app = Flask(__name__)
api = Api(app, doc="/swagger/")
api.add_resource(MentionAcceptResource, "/mentions/<int:mention_id>/accept")
api.add_resource(MentionRejectResource, "/mentions/<int:mention_id>/reject")
class TestMentionRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    @patch("app.routes.mention_routes.mention_service")
    def test_accept_mention_success(self, mock_mention_service):
        mention_id = 1
        document_edit_id = 2
        mock_mention_service.accept_mention.return_value = {"message": "Mention accepted"}
        response = self.client.post(
            f"/mentions/{mention_id}/accept",
            query_string={"document_edit_id": document_edit_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Mention accepted"})
        mock_mention_service.accept_mention.assert_called_once_with(mention_id, document_edit_id)
    @patch("app.routes.mention_routes.mention_service")
    def test_accept_mention_missing_document_edit_id(self, mock_mention_service):
        mention_id = 1
        response = self.client.post(f"/mentions/{mention_id}/accept")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])
    @patch("app.routes.mention_routes.mention_service")
    def test_reject_mention_success(self, mock_mention_service):
        mention_id = 1
        document_edit_id = 2
        mock_mention_service.reject_mention.return_value = {"message": "Mention rejected"}
        response = self.client.post(
            f"/mentions/{mention_id}/reject",
            query_string={"document_edit_id": document_edit_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Mention rejected"})
        mock_mention_service.reject_mention.assert_called_once_with(mention_id, document_edit_id)
    @patch("app.routes.mention_routes.mention_service")
    def test_reject_mention_missing_document_edit_id(self, mock_mention_service):
        mention_id = 1
        response = self.client.post(f"/mentions/{mention_id}/reject")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])