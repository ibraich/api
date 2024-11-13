import unittest
from app import create_app

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_api_home(self):
        response = self.client.get('/api')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, Flask API is running!', response.data)