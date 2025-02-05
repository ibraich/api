import unittest
import json
from app import app
from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository


class TestJaccardIndexEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.headers = {"Content-Type": "application/json"}
        self.service = DocumentService(DocumentRepository())

    def test_jaccard_index_success(self):
        payload = {
            "document": {
                "tokens": [{"text": "word1"}, {"text": "word2"}, {"text": "word3"}]
            },
            "document_edits": [
                {"tokens": [{"text": "word1"}, {"text": "word2"}]},
                {"tokens": [{"text": "word2"}, {"text": "word3"}, {"text": "word4"}]},
            ],
        }
        response = self.app.post(
            "/difference-calc/jaccard", headers=self.headers, data=json.dumps(payload)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("jaccard_index", data)

    def test_jaccard_index_missing_payload(self):
        response = self.app.post(
            "/difference-calc/jaccard", headers=self.headers, data=json.dumps({})
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_jaccard_index_invalid_format(self):
        response = self.app.post(
            "/difference-calc/jaccard", headers=self.headers, data="invalid json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
