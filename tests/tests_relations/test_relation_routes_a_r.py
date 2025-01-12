import unittest
from flask import Flask
from flask_restx import Api
from relation_routes import ns as relation_ns
from unittest.mock import patch

class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        # Flask-App und Namespace für Tests initialisieren
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(relation_ns)
        self.client = self.app.test_client()

    @patch('services.relation_service.RelationService.accept_relation')
    def test_accept_relation_success(self, mock_accept_relation):
        mock_accept_relation.return_value = None
        response = self.client.post('/relation/relation123/accept')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully accepted', response.json['message'])

    @patch('services.relation_service.RelationService.reject_relation')
    def test_reject_relation_success(self, mock_reject_relation):
        mock_reject_relation.return_value = None
        response = self.client.post('/relation/relation123/reject')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully rejected', response.json['message'])

    @patch('services.relation_service.RelationService.accept_relation')
    def test_accept_relation_not_found(self, mock_accept_relation):
        mock_accept_relation.side_effect = Exception('Relation not found.')
        response = self.client.post('/relation/invalid_id/accept')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Relation not found', response.json['error'])

    @patch('services.relation_service.RelationService.reject_relation')
    def test_reject_relation_bad_request(self, mock_reject_relation):
        mock_reject_relation.side_effect = Exception('Bad Request.')
        response = self.client.post('/relation/invalid_id/reject')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Bad Request', response.json['error'])