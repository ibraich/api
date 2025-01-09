
import unittest
from app import create_app, db
from flask import json

class TestRelationRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_accept_relation(self):
        response = self.client.post("/relation/1/accept", headers={"X-User-ID": "1"})
        self.assertEqual(response.status_code, 200)

    def test_reject_relation(self):
        response = self.client.post("/relation/1/reject", headers={"X-User-ID": "1"})
        self.assertEqual(response.status_code, 200)
