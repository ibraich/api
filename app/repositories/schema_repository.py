from app.models import Schema
from app.repositories.base_repository import BaseRepository
from app.db import db


class SchemaRepository(BaseRepository):
    def check_schema_exists(self, schema_id):
        if super().get_object_by_id(Schema, schema_id) is None:
            response = {"message": "Schema does not exist"}
            return response, 400
        return "", 200
