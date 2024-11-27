from app.db import db
from app.models import Schema


class SchemaService:

    @staticmethod
    def check_schema_exists(schema_id):
        if db.session.query(Schema).filter(Schema.id == schema_id).first is None:
            response = {"message": "Schema does not exist"}
            return response, 400
        return "", 200


schema_service = SchemaService()
