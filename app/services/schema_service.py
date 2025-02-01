import random
import re
import typing

from werkzeug.exceptions import NotFound, BadRequest, Conflict

from app.models import Schema, SchemaMention, SchemaRelation, SchemaConstraint
from app.repositories.schema_repository import SchemaRepository
from app.services.user_service import UserService, user_service


class SchemaService:
    __schema_repository: SchemaRepository
    user_service: UserService

    def __init__(self, schema_repository, user_service):
        self.__schema_repository = schema_repository
        self.user_service = user_service

    def check_schema_exists(self, schema_id):
        if self.__schema_repository.get_schema_by_id(schema_id) is None:
            return NotFound("Schema not found")

    def get_schema_by_id(self, schema_id):
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
            "models": self.get_models_by_schema(schema.id),
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

    def get_schemas_by_user(self, user_id):
        schemas = self.__schema_repository.get_schema_ids_by_user(user_id)
        if schemas is None:
            return {"schemas": []}
        return {"schemas": [self.get_schema_by_id(schema.id) for schema in schemas]}

    def create_schema(self, modelling_language_id, team_id, name) -> Schema:
        schema = self.__schema_repository.create_schema(
            modelling_language_id, team_id, name
        )
        steps = self.__schema_repository.get_model_steps()
        steps = [step.type for step in steps]
        schema.models = self.__schema_repository.add_model_to_schema(
            schema.id, "OpenAI Large Language Model", "llm", steps
        )
        return schema

    def create_schema_mention(
        self,
        schema_id: int,
        tag: str,
        description: str,
        entity_possible: bool,
        color: typing.Optional[str] = None,
    ) -> SchemaMention:
        if color is None or not self.validate_color_code(color):
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
        self, schema, schema_relation_id, head_schema_mention_id, tail_schema_mention_id
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
                    )
                    or (
                        constraint["schema_mention_tail"]["id"]
                        == head_schema_mention_id
                        and constraint["schema_mention_head"]["id"]
                        == tail_schema_mention_id
                        and constraint["is_directed"] == False
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

    def create_extended_schema(self, schema, team_id: int) -> any:
        modelling_language = self.__schema_repository.get_modelling_laguage_by_name(
            schema["modelling_language"]
        )
        if modelling_language is None:
            raise BadRequest("Modelling Language not allowed")

        if self.__has_duplicates(schema["schema_mentions"], key="tag"):
            raise Conflict("Duplicate tags found in schema mentions.")
        if self.__has_duplicates(schema["schema_relations"], key="tag"):
            raise Conflict("Duplicate tags found in schema relations.")
        if self.__has_duplicates(
            schema["schema_constraints"],
            key=lambda x: (
                x["mention_head_tag"],
                x["mention_tail_tag"],
                x["relation_tag"],
            ),
        ):
            raise Conflict("Duplicate constraints found in schema.")

        created_schema = self.create_schema(
            modelling_language.id, team_id, schema["name"]
        )

        schema_mentions_by_tag = {}
        for schema_mention in schema["schema_mentions"]:
            created_mention = self.create_schema_mention(
                created_schema.id,
                schema_mention.get("tag"),
                schema_mention.get("description"),
                schema_mention.get("entity_possible"),
                schema_mention.get("color"),
            )
            schema_mentions_by_tag[schema_mention["tag"]] = created_mention

        schema_relations_by_tag = {}
        for schema_relation in schema["schema_relations"]:
            created_relation = self.create_schema_relation(
                created_schema.id,
                schema_relation.get("tag"),
                schema_relation.get("description"),
            )
            schema_relations_by_tag[schema_relation["tag"]] = created_relation

        for constraint in schema["schema_constraints"]:
            self.create_schema_constraint(
                schema_relations_by_tag[constraint.get("relation_tag")].id,
                schema_mentions_by_tag[constraint.get("mention_head_tag")].id,
                schema_mentions_by_tag[constraint.get("mention_tail_tag")].id,
                constraint.get("is_directed"),
            )

        return self.get_schema_by_id(created_schema.id)

    def __has_duplicates(self, items, key):
        seen = set()
        for item in items:
            identifier = key(item) if callable(key) else item[key]
            if identifier in seen:
                return True
            seen.add(identifier)
        return False

    def validate_color_code(self, string):
        hexa_code = re.compile(r"^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$")
        return bool(re.match(hexa_code, string))

    def train_model_for_schema(self, schema_id, model_name, model_type, steps):
        duplicate = self.__schema_repository.get_model_by_name(model_name)
        if duplicate is not None:
            raise BadRequest("Model Name already exists")

        # TODO call training endpoint

        models = self.__schema_repository.add_model_to_schema(
            schema_id, model_name, model_type, steps
        )
        return {
            "models": [
                {
                    "id": model.id,
                    "name": model.model_name,
                    "type": model.model_type,
                    "step": {
                        "id": model.model_step_id,
                        "type": model.model_step_name,
                    },
                    "schema_id": model.schema_id,
                }
                for model in models
            ]
        }

    def check_models_in_schema(
        self, mention_model_id, entity_model_id, relation_model_id, schema_id
    ):
        schema_models = self.__schema_repository.get_models_by_schema(schema_id)
        validated = 0
        for schema_model in schema_models:
            if (
                schema_model.id == mention_model_id
                and schema_model.model_step_id == 1  # "MENTIONS"
            ):
                validated += 1
            if (
                schema_model.id == entity_model_id
                and schema_model.model_step_id == 2  # "ENTITIES"
            ):
                validated += 1
            if (
                schema_model.id == relation_model_id
                and schema_model.model_step_id == 3  # "RELATIONS"
            ):
                validated += 1

        if validated != 3:
            raise BadRequest(
                "At least one model not found for given steps in this schema"
            )

    def get_models_by_schema(self, schema_id):
        models = self.__schema_repository.get_models_by_schema(schema_id)
        return [
            {
                "id": model.id,
                "name": model.model_name,
                "type": model.model_type,
                "step": {
                    "id": model.model_step_id,
                    "type": model.model_step_name,
                },
            }
            for model in models
        ]

    def get_schema_mentions_by_schema(self, schema_id):
        schema_mentions = self.__schema_repository.get_schema_mentions_by_schema(
            schema_id
        )
        if schema_mentions is None:
            raise BadRequest("No Schema Mentions Found")
        return schema_mentions

    def get_schema_by_document(self, document_id):
        return self.__schema_repository.get_schema_by_document(document_id)

    def get_schema_relations_by_schema(self, schema_id):
        schema_relations = self.__schema_repository.get_schema_relations_by_schema(
            schema_id
        )
        if schema_relations is None:
            raise BadRequest("No Schema Mentions Found")
        return schema_relations

    def get_schema_constraints_by_schema(self, schema_id):
        schema_constraints = self.__schema_repository.get_schema_constraints_by_schema(
            schema_id
        )
        if schema_constraints is None:
            raise BadRequest("No Schema Mentions Found")
        return schema_constraints


schema_service = SchemaService(SchemaRepository(), user_service)
