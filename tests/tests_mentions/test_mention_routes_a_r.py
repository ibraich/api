import unittest
from flask import Flask
from flask_restx import Api
from mention_routes import ns as mention_ns
from unittest.mock import patch

class TestMentionRoutes(unittest.TestCase):
    def setUp(self):
        # Flask-App und Namespace für Tests initialisieren
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(mention_ns)
        self.client = self.app.test_client()

    @patch('services.mention_service.MentionService.accept_mention')
    def test_accept_mention_success(self, mock_accept_mention):
        mock_accept_mention.return_value = None
        response = self.client.post('/mention/mention123/accept')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully accepted', response.json['message'])

    @patch('services.mention_service.MentionService.reject_mention')
    def test_reject_mention_success(self, mock_reject_mention):
        mock_reject_mention.return_value = None
        response = self.client.post('/mention/mention123/reject')
        self.assertEqual(response.status_code, 200)
        self.assertIn('successfully rejected', response.json['message'])

    @patch('services.mention_service.MentionService.accept_mention')
    def test_accept_mention_not_found(self, mock_accept_mention):
        mock_accept_mention.side_effect = Exception('Mention not found.')
        response = self.client.post('/mention/invalid_id/accept')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mention not found', response.json['error'])

    @patch('services.mention_service.MentionService.reject_mention')
    def test_reject_mention_bad_request(self, mock_reject_mention):
        mock_reject_mention.side_effect = Exception('Bad Request.')
        response = self.client.post('/mention/invalid_id/reject')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Bad Request', response.json['error'])