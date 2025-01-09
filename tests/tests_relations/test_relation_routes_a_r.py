
import unittest
from app import create_app

class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_accept_relation(self):
        response = self.client.post('/relations/1/accept', query_string={'document_edit_id': 1})
        self.assertEqual(response.status_code, 200)

    def test_reject_relation(self):
        response = self.client.post('/relations/1/reject', query_string={'document_edit_id': 1})
        self.assertEqual(response.status_code, 200)
