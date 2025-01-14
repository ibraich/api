import unittest
from unittest.mock import patch
from flask import Flask
from flask_restx import Api
from app.routes.relation_routes import RelationAcceptResource, RelationRejectResource

# Flask-App und API für Tests erstellen
app = Flask(__name__)
api = Api(app, doc="/swagger/")
api.add_resource(RelationAcceptResource, "/relations/<int:relation_id>/accept")
api.add_resource(RelationRejectResource, "/relations/<int:relation_id>/reject")


class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.routes.relation_routes.relation_service")
    def test_accept_relation_success(self, mock_relation_service):
        relation_id = 1
        document_edit_id = 2
        mock_relation_service.accept_relation.return_value = {"message": "Relation accepted"}

        response = self.client.post(
            f"/relations/{relation_id}/accept",
            query_string={"document_edit_id": document_edit_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Relation accepted"})
        mock_relation_service.accept_relation.assert_called_once_with(relation_id, document_edit_id)

    @patch("app.routes.relation_routes.relation_service")
    def test_accept_relation_missing_document_edit_id(self, mock_relation_service):
        relation_id = 1

        response = self.client.post(f"/relations/{relation_id}/accept")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])

    @patch("app.routes.relation_routes.relation_service")
    def test_reject_relation_success(self, mock_relation_service):
        relation_id = 1
        document_edit_id = 2
        mock_relation_service.reject_relation.return_value = {"message": "Relation rejected"}

        response = self.client.post(
            f"/relations/{relation_id}/reject",
            query_string={"document_edit_id": document_edit_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Relation rejected"})
        mock_relation_service.reject_relation.assert_called_once_with(relation_id, document_edit_id)

    @patch("app.routes.relation_routes.relation_service")
    def test_reject_relation_missing_document_edit_id(self, mock_relation_service):
        relation_id = 1

        response = self.client.post(f"/relations/{relation_id}/reject")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Document Edit ID is required", response.json["message"])
