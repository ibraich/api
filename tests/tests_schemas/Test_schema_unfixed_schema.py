import unittest
from unittest.mock import MagicMock

from app.services.schema_service import SchemaService
from werkzeug.exceptions import BadRequest


class TestSchemaService(unittest.TestCase):
    def setUp(self):
        self.schema_repository = MagicMock()
        self.schema_service = SchemaService(self.schema_repository)

    def test_update_schema_success(self):
        schema_id = 1
        mentions = [{"id": 2, "name": "Mention1"}]
        relations = [{"id": 3, "name": "Relation1"}]
        constraints = [{"id": 4, "name": "Constraint1"}]

        self.schema_repository.get_schema_by_id.return_value = MagicMock(
            isFixed=False, mentions=[], relations=[], constraints=[]
        )

        self.schema_service.update_schema(schema_id, mentions, relations, constraints)

        self.schema_repository.add_schema_elements.assert_called_once_with(
            schema_id, mentions, relations, constraints
        )
        self.schema_repository.remove_schema_elements.assert_not_called()

    def test_update_schema_fixed(self):
        schema_id = 1
        mentions = []
        relations = []
        constraints = []

        self.schema_repository.get_schema_by_id.return_value = MagicMock(isFixed=True)

        with self.assertRaises(BadRequest):
            self.schema_service.update_schema(
                schema_id, mentions, relations, constraints
            )

    def test_update_schema_not_found(self):
        schema_id = 1
        mentions = []
        relations = []
        constraints = []

        self.schema_repository.get_schema_by_id.return_value = None

        with self.assertRaises(BadRequest):
            self.schema_service.update_schema(
                schema_id, mentions, relations, constraints
            )


if __name__ == "__main__":
    unittest.main()
