
from http.client import BAD_REQUEST
import unittest
from unittest.mock import MagicMock
from app.models import Schema

from app.routes.schema_routes import SchemaResource


class TestSchemaResource(unittest.TestCase):
    def setUp(self):
        self.schema_service = MagicMock()
        self.schema_resource = SchemaResource(self.schema_service)
        self.schema_service.create_schema.return_value = Schema(
            id=1, name="Test Schema", team_id=1, mentions=[], relations=[], constraints=[]
        )

    def test_post_success(self):
        with unittest.mock.patch("flask.request.json", return_value={
            "team_id": 1,
            "schema_data": {"name": "Test Schema"},
            "mentions": [{"tag": "mention1"}],
            "relations": [{"tag": "relation1"}],
            "constraints": [{"head": "mention1", "tail": "mention2", "relation": "relation1"}]
        }):
            response, status = self.schema_resource.post()
            self.assertEqual(status, 201)
            self.schema_service.create_schema.assert_called_once()

    def test_post_missing_field(self):
        with unittest.mock.patch("flask.request.json", return_value={}):
            with self.assertRaises(BAD_REQUEST):
                self.schema_resource.post()

if __name__ == "__main__":
    unittest.main()
