from flask_restx import fields
from app.extension import api

mention_input_dto = api.model(
    "mention",
    {
        "tag": fields.String,
        "document_edit_id": fields.Integer,
        "token_ids": fields.List(fields.Integer),
    },
)

mention_output_dto = api.model(
    "mention_output",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "is_shown_recommendation": fields.Boolean,
        "document_edit_id": fields.Integer,
        "document_recommendation_id": fields.Integer,
        "entity_id": fields.Integer,
    },
)

create_project_input_model = api.model(
    "CreateProject",
    {
        "name": fields.String(required=True),
        "user_id": fields.Integer(required=True),
        "team_id": fields.Integer(required=True),
        "schema_id": fields.Integer(required=True),
    },
)

create_project_output_model = api.model(
    "CreateProjectOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator_id": fields.Integer,
        "team_id": fields.Integer,
        "schema_id": fields.Integer,
    },
)
