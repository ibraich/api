from flask_restx import fields
from app.extension import api

mention_input_dto = api.model(
    "CreateMentionInput",
    {
        "tag": fields.String(required=True),
        "document_edit_id": fields.Integer(required=True),
        "token_ids": fields.List(fields.Integer, required=True),
    },
)

mention_output_dto = api.model(
    "MentionOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "is_shown_recommendation": fields.Boolean,
        "document_edit_id": fields.Integer,
        "document_recommendation_id": fields.Integer,
        "entity_id": fields.Integer,
    },
)

project_input_dto = api.model(
    "ProjectInput",
    {
        "name": fields.String(required=True),
        "team_id": fields.Integer(required=True, min=1),
        "schema_id": fields.Integer(required=True, min=1),
    },
)

project_output_dto = api.model(
    "ProjectOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator_id": fields.Integer,
        "team_id": fields.Integer,
        "schema_id": fields.Integer,
    },
)

document_output_dto = api.model(
    "DocumentOutput",
    {
        "id": fields.Integer,
        "content": fields.String,
        "name": fields.String,
        "team_id": fields.Integer,
        "team_name": fields.String,
        "schema_id": fields.Integer,
        "project_id": fields.Integer,
        "project_name": fields.String,
        "document_edit_id": fields.Integer,
        "document_edit_state": fields.String,
    },
)

entity_output_dto = api.model(
    "EntityOutput",
    {
        "id": fields.Integer,
        "isShownRecommendation": fields.Boolean,
        "document_edit_id": fields.Integer,
        "document_recommendation_id": fields.Integer,
    },
)

entity_output_list_dto = api.model(
    "EntityOutputList",
    {
        "entities": fields.List(fields.Nested(entity_output_dto)),
    },
)

mention_output_list_dto = api.model(
    "MentionOutputList",
    {
        "mentions": fields.List(fields.Nested(mention_output_dto)),
    },
)

relation_output_dto = api.model(
    "RelationOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "isShownRecommendation": fields.Boolean,
        "isDirected": fields.Boolean,
        "mention_head_id": fields.Integer,
        "mention_tail_id": fields.Integer,
    },
)

relation_output_list_dto = api.model(
    "RelationOutputList",
    {
        "relations": fields.List(fields.Nested(relation_output_dto)),
    },
)


schema_mention_output_dto = api.model(
    "SchemaMentionOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "description": fields.String,
        "color": fields.String,
        "entity_possible": fields.Boolean,
    },
)

schema_relation_output_dto = api.model(
    "SchemaRelationOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "description": fields.String,
    },
)

schema_constraint_output_dto = api.model(
    "SchemaConstraintOutput",
    {
        "id": fields.Integer,
        "is_directed": fields.Boolean,
        "schema_relation": fields.Nested(schema_relation_output_dto),
        "schema_mention_head": fields.Nested(schema_mention_output_dto),
        "schema_mention_tail": fields.Nested(schema_mention_output_dto),
    },
)

schema_output_dto = api.model(
    "SchemaOutput",
    {
        "id": fields.Integer,
        "is_fixed": fields.Boolean,
        "modellingLanguage": fields.String,
        "team_id": fields.Integer,
        "team_name": fields.String,
        "schema_mentions": fields.List(fields.Nested(schema_mention_output_dto)),
        "schema_relations": fields.List(fields.Nested(schema_relation_output_dto)),
        "schema_constraints": fields.List(fields.Nested(schema_constraint_output_dto)),
    },
)

schema_output_list_dto = api.model(
    "SchemaOutputList",
    {
        "schemas": fields.List(fields.Nested(schema_output_dto)),
    },
)
