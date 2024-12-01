from werkzeug.exceptions import NotFound

from app.repositories.schema_repository import SchemaRepository


class SchemaService:
    __schema_repository: SchemaRepository

    def __init__(self, schema_repository: SchemaRepository):
        self.__schema_repository = schema_repository

    def check_schema_exists(self, schema_id):
        if self.__schema_repository.get_schema_by_id(schema_id) is None:
            return NotFound("Schema not found")


schema_service = SchemaService(SchemaRepository())
