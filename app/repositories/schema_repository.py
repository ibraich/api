from app.models import Schema
from app.repositories.base_repository import BaseRepository
from app.db import db


class SchemaRepository(BaseRepository):
    def get_schema_by_id(self, schema_id):
        super().get_object_by_id(Schema, schema_id)
