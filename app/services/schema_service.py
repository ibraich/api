from app.repositories.schema_repository import SchemaRepository


class SchemaService:
    __schema_repository: SchemaRepository

    def __init__(self, schema_repository: SchemaRepository):
        self.__schema_repository = schema_repository

    def check_schema_exists(self, schema_id):
        return self.__schema_repository.check_schema_exists(schema_id)


schema_service = SchemaService(SchemaRepository())
