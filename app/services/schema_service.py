import typing
import random

from werkzeug.exceptions import NotFound, BadRequest

from app.models import Schema, SchemaMention, SchemaRelation, SchemaConstraint, Mention
from app.repositories.schema_repository import SchemaRepository
from app.services.user_service import UserService, user_service


class SchemaService:
    __schema_repository: SchemaRepository
    user_service: UserService

    def __init__(self, schema_repository: SchemaRepository, user_service: UserService):
        self.__schema_repository = schema_repository
        self.user_service = user_service

    def check_schema_exists(self, schema_id):
        if self.__schema_repository.get_schema_by_id(schema_id) is None:
            return NotFound("Schema not found")

    def get_schema_by_id(self, schema_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_schema_accessible(user_id, schema_id)
        schema = self.__schema_repository.get_schema_by_id(schema_id)
        if schema is None:
            raise BadRequest("Schema not found")
        return self._build_schema(schema)

    def get_schema_by_project_id(self, project_id):
        schema = self.__schema_repository.get_by_project(project_id)
        if schema is None:
            raise BadRequest("Project not found")
        return self._build_schema(schema)

    def _build_schema(self, schema):
        constraints = self.__schema_repository.get_schema_constraints_by_schema(
            schema.id
        )
        mentions = self.__schema_repository.get_schema_mentions_by_schema(schema.id)
        relations = self.__schema_repository.get_schema_relations_by_schema(schema.id)
        return {
            "id": schema.id,
            "name": schema.name,
            "is_fixed": schema.isFixed,
            "modellingLanguage": schema.modelling_language,
            "team_id": schema.team_id,
            "team_name": schema.team_name,
            "schema_mentions": [
                {
                    "id": mention.id,
                    "tag": mention.tag,
                    "description": mention.description,
                    "color": mention.color,
                    "entityPossible": mention.entityPossible,
                }
                for mention in mentions
            ],
            "schema_relations": [
                {
                    "id": relation.id,
                    "tag": relation.tag,
                    "description": relation.description,
                }
                for relation in relations
            ],
            "schema_constraints": [
                {
                    "id": constraint.id,
                    "is_directed": constraint.isDirected,
                    "schema_relation": {
                        "id": constraint.relation_id,
                        "tag": constraint.relation_tag,
                        "description": constraint.relation_description,
                    },
                    "schema_mention_head": {
                        "id": constraint.mention_head_id,
                        "tag": constraint.mention_head_tag,
                        "description": constraint.mention_head_description,
                        "color": constraint.mention_head_color,
                        "entityPossible": constraint.mention_head_entityPossible,
                    },
                    "schema_mention_tail": {
                        "id": constraint.mention_tail_id,
                        "tag": constraint.mention_tail_tag,
                        "description": constraint.mention_tail_description,
                        "color": constraint.mention_tail_color,
                        "entityPossible": constraint.mention_tail_entityPossible,
                    },
                }
                for constraint in constraints
            ],
        }

    def get_schemas_by_user(self):
        user_id = self.user_service.get_logged_in_user_id()
        schemas = self.__schema_repository.get_schema_ids_by_user(user_id)
        if schemas is None:
            return {"schemas": []}
        return {"schemas": [self.get_schema_by_id(schema.id) for schema in schemas]}

    def create_schema(self, modelling_language_id, team_id, name) -> Schema:
        return self.__schema_repository.create_schema(
            modelling_language_id, team_id, name
        )

    def create_schema_mention(
        self,
        schema_id: int,
        tag: str,
        description: str,
        entity_possible: bool,
        color: typing.Optional[str] = None,
    ) -> SchemaMention:
        if color is None:
            color = self.generate_random_hex_color()
        return self.__schema_repository.create_schema_mention(
            schema_id, tag, description, entity_possible, color
        )

    def create_schema_relation(
        self, schema_id, tag: str, description: str
    ) -> SchemaRelation:
        return self.__schema_repository.create_schema_relation(
            schema_id, tag, description
        )

    def create_schema_constraint(
        self,
        schema_relation_id: int,
        schema_mention_id_head: int,
        schema_mention_id_tail: int,
        is_directed: bool,
    ) -> SchemaConstraint:
        return self.__schema_repository.create_schema_constraint(
            schema_relation_id,
            schema_mention_id_head,
            schema_mention_id_tail,
            is_directed,
        )

    def verify_constraint(
        self,
        schema,
        schema_relation_id,
        head_schema_mention_id,
        tail_schema_mention_id,
        is_directed=False,
    ) -> any:
        constraint = next(
            (
                constraint
                for constraint in schema["schema_constraints"]
                if constraint["schema_relation"]["id"] == schema_relation_id
                and (
                    (
                        constraint["schema_mention_head"]["id"]
                        == head_schema_mention_id
                        and constraint["schema_mention_tail"]["id"]
                        == tail_schema_mention_id
                        and constraint["is_directed"] == is_directed
                    )
                    or (
                        constraint["schema_mention_tail"]["id"]
                        == head_schema_mention_id
                        and constraint["schema_mention_head"]["id"]
                        == tail_schema_mention_id
                        and constraint["is_directed"] == False
                        and is_directed == False
                    )
                )
            ),
            None,
        )
        if constraint is None:
            raise BadRequest(
                "The Relation "
                + str(schema_relation_id)
                + " with mention_head: "
                + str(head_schema_mention_id)
                + " and mention_tail: "
                + str(tail_schema_mention_id)
                + " is not allowed in the schema."
            )

        return constraint

    def generate_random_hex_color(self):
        """Generate a random hexadecimal color code."""
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def verify_entity_possible(self, schema_id, tag):
        schema_mention = self.__schema_repository.get_schema_mention_by_schema_tag(
            schema_id, tag
        )
        if schema_mention is None:
            raise BadRequest("Mention Tag not allowed")
        if schema_mention.entityPossible is False:
            raise BadRequest("Entity not allowed for this mention")

    def get_schema_by_document_edit(self, document_edit_id):
        return self.__schema_repository.get_schema_by_document_edit(document_edit_id)

    def fix_schema(self, schema_id):
        self.__schema_repository.fix_schema(schema_id)

    def get_schema_mention_by_id(self, schema_mention_id):
        schema_mention = self.__schema_repository.get_schema_mention_by_id(
            schema_mention_id
        )
        if schema_mention is None:
            raise BadRequest("Mention Tag not allowed")
        return schema_mention

    def get_schema_relation_by_id(self, schema_relation_id):
        schema_relation = self.__schema_repository.get_schema_relation_by_id(
            schema_relation_id
        )
        if schema_relation is None:
            raise BadRequest("Relation Tag not allowed")
        return schema_relation


schema_service = SchemaService(SchemaRepository(), user_service)
