import unittest
from unittest.mock import patch
from app import create_app
from app.config import TestingConfig


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.patcher = patch(
            "flask_jwt_extended.view_decorators.verify_jwt_in_request",
            return_value=None,
        )
        self.mock_function = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
