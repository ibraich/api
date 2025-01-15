import typing
import random

from werkzeug.exceptions import NotFound, BadRequest, Conflict

from app.models import Schema, SchemaMention, SchemaRelation, SchemaConstraint
from app.repositories.schema_repository import SchemaRepository
from app.services.user_service import UserService, user_service


def generate_random_hex_color():
    """Generate a random hexadecimal color code."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


class SchemaService:
    __schema_repository: SchemaRepository
    user_service: UserService

    def __init__(self, schema_repository: SchemaRepository, user_service: UserService):
        self.__schema_repository = schema_repository
        self.user_service = user_service
        self.schema_repo = SchemaRepository()
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
                    "entity_possible": mention.entityPossible,
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
                        "entity_possible": constraint.mention_head_entityPossible,
                    },
                    "schema_mention_tail": {
                        "id": constraint.mention_tail_id,
                        "tag": constraint.mention_tail_tag,
                        "description": constraint.mention_tail_description,
                        "color": constraint.mention_tail_color,
                        "entity_possible": constraint.mention_tail_entityPossible,
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
            color = generate_random_hex_color()
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

    def create_schema(self, team_id, user_id, name, modelling_language_id, mentions, relations, constraints):
        """
        Create a schema with mentions, relations, and constraints.
        """
        # Check if the user belongs to the team
        if not self.user_service.check_user_in_team(user_id, team_id):
            raise BadRequest("User does not belong to the specified team.")

        # Ensure the schema has unique tags and constraints
        if len(set(m['tag'] for m in mentions)) != len(mentions):
            raise BadRequest("Duplicate tags found in mentions.")
        if len(set(r['tag'] for r in relations)) != len(relations):
            raise BadRequest("Duplicate tags found in relations.")
        if len(set((c['head'], c['tail'], c['relation']) for c in constraints)) != len(constraints):
            raise BadRequest("Duplicate constraints found.")

        # Insert the schema and related data
        schema_id = self.__schema_repository.create_schema(team_id, name, modelling_language_id)
        self.__schema_repository.create_schema_mentions(schema_id, mentions)
        self.__schema_repository.create_schema_relations(schema_id, relations)
        self.__schema_repository.create_schema_constraints(schema_id, constraints)

        return schema_id   

schema_service = SchemaService(SchemaRepository(), user_service)
