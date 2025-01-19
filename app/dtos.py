from flask_restx import fields
from app.extension import api

mention_input_dto = api.model(
    "CreateMentionInput",
    {
        "schema_mention_id": fields.Integer(required=True),
        "document_edit_id": fields.Integer(required=True),
        "token_ids": fields.List(fields.Integer, required=True),
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

mention_output_dto = api.model(
    "MentionOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "is_shown_recommendation": fields.Boolean,
        "document_edit_id": fields.Integer,
        "document_recommendation_id": fields.Integer,
        "entity_id": fields.Integer,
        "tokens": fields.List(fields.Integer),
        "schema_mention": fields.Nested(schema_mention_output_dto),
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

team_dto = api.model(
    "Team",
    {
        "team_id": fields.Integer,
        "team_name": fields.String,
    },
)

schema_dto = api.model(
    "Schema",
    {
        "schema_id": fields.Integer,
        "schema_name": fields.String,
    },
)

project_dto = api.model(
    "Project",
    {
        "project_id": fields.Integer,
        "project_name": fields.String,
    },
)

document_edit_dto = api.model(
    "DocumentEdit",
    {
        "document_edit_id": fields.Integer,
        "document_edit_state": fields.String,
    },
)

document_list_dto = api.model(
    "DocumentList",
    {
        "id": fields.Integer,
        "content": fields.String,
        "name": fields.String,
        "project": fields.Nested(project_dto),
        "schema": fields.Nested(schema_dto),
        "team": fields.Nested(team_dto),
        "document_edit": fields.Nested(document_edit_dto),
    },
)

document_output_dto = api.model(
    "DocumentOutput",
    {
        "documents": fields.List(fields.Nested(document_list_dto)),
    },
)


entity_input_dto = api.model(
    "EntityInput",
    {
        "document_edit_id": fields.Integer(required=True),
        "mention_ids": fields.List(fields.Integer, required=True),
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

schema_relation_output_dto = api.model(
    "SchemaRelationOutput",
    {
        "id": fields.Integer,
        "tag": fields.String,
        "description": fields.String,
        "schema_id": fields.Integer,
    },
)

relation_input_dto = api.model(
    "RelationInput",
    {
        "schema_relation_id": fields.Integer,
        "document_edit_id": fields.Integer(required=True),
        "isDirected": fields.Boolean,
        "mention_head_id": fields.Integer(required=True),
        "mention_tail_id": fields.Integer(required=True),
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
        "schema_relation": fields.Nested(schema_relation_output_dto),
    },
)

relation_output_list_dto = api.model(
    "RelationOutputList",
    {
        "relations": fields.List(fields.Nested(relation_output_dto)),
    },
)

document_create_dto = api.model(
    "DocumentUpload",
    {
        "project_id": fields.Integer(required=True, description="ID of the project"),
        "file_name": fields.String(required=True, description="Name of the document"),
        "file_content": fields.String(
            required=True, description="Content of the document"
        ),
    },
)

document_create_output_dto = api.model(
    "DocumentUploadOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "content": fields.String,
        "creator_id": fields.Integer,
        "project_id": fields.Integer,
        "state_id": fields.Integer,
    },
)

user_output_dto = api.model(
    "UserOutput",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
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
        "name": fields.String,
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

team_member_input_dto = api.model(
    "TeamMemberInput",
    {
        "user_mail": fields.String(required=True),
        "team_id": fields.Integer(required=True),
    },
)

team_member_output_dto = api.model(
    "TeamMemberOutput",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
    },
)

team_input_dto = api.model(
    "TeamInput",
    {
        "name": fields.String(required=True),
    },
)

team_output_dto = api.model(
    "TeamOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator_id": fields.Integer,
    },
)

team_user_output_dto = api.model(
    "TeamUserOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator_id": fields.Integer,
        "members": fields.List(fields.Nested(user_output_dto)),
    },
)

document_edit_input_dto = api.model(
    "DocumentInput",
    {
        "document_id": fields.Integer(required=True, min=1),
    },
)

team_user_output_list_dto = api.model(
    "TeamUserListOutput",
    {
        "teams": fields.List(fields.Nested(team_user_output_dto)),
    },
)

document_edit_output_dto = api.model(
    "DocumentEditOutput",
    {
        "id": fields.Integer,
        "schema_id": fields.Integer,
        "document_id": fields.Integer,
    },
)


token_output_dto = api.model(
    "Token",
    {
        "id": fields.Integer(required=True),
        "text": fields.String(required=True),
        "document_index": fields.Integer,
        "sentence_index": fields.Integer,
        "pos_tag": fields.String,
    },
)

document_edit_mention_output_dto = api.model(
    "Mention",
    {
        "id": fields.Integer(required=True),
        "tag": fields.String(required=True),
        "tokens": fields.List(fields.Nested(token_output_dto), required=True),
        "entity": fields.Nested(
            api.model(
                "Entity",
                {
                    "id": fields.Integer(required=True),
                },
            )
        ),
        "schema_mention": fields.Nested(schema_mention_output_dto),
    },
)
document_edit_user_output_dto = api.model(
    "User",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
    },
)
document_edit_get_output_dto = api.model(
    "DocumentEditGetOutput",
    {
        "document": fields.Nested(
            api.model(
                "Document",
                {
                    "id": fields.Integer,
                    "tokens": fields.List(fields.Nested(token_output_dto)),
                    "creator": fields.Nested(document_edit_user_output_dto),
                    "state": fields.Nested(
                        api.model(
                            "State",
                            {
                                "id": fields.Integer,
                                "type": fields.String(required=False),
                            },
                        )
                    ),
                    "project": fields.Nested(
                        api.model(
                            "Project",
                            {
                                "id": fields.Integer,
                                "name": fields.String,
                                "creator": fields.Nested(document_edit_user_output_dto),
                            },
                        )
                    ),
                },
            )
        ),
        "user": fields.Nested(document_edit_user_output_dto),
        "state": fields.Nested(
            api.model(
                "DocumentEditState",
                {
                    "id": fields.Integer,
                    "type": fields.String(required=False),
                },
            )
        ),
        "mentions": fields.List(
            fields.Nested(document_edit_mention_output_dto), required=False
        ),
        "relations": fields.List(
            fields.Nested(
                api.model(
                    "Relation",
                    {
                        "id": fields.Integer(required=True),
                        "tag": fields.String(required=True),
                        "mention_head": fields.Nested(document_edit_mention_output_dto),
                        "mention_tail": fields.Nested(document_edit_mention_output_dto),
                        "schema_relation": fields.Nested(schema_relation_output_dto),
                    },
                ),
                required=False,
            )
        ),
    },
)

project_list_dto = api.model(
    "project_list_dto",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator_id": fields.Integer,
        "team": fields.Nested(team_dto),
        "schema": fields.Nested(schema_dto),
    },
)

project_user_output_list_dto = api.model(
    "project_user_output_list_dto",
    {
        "projects": fields.List(fields.Nested(project_list_dto)),
    },
)

signup_input_dto = api.model(
    "SignupInput",
    {
        "username": fields.String(
            required=True, description="Username of the new user"
        ),
        "email": fields.String(required=True, description="Email of the new user"),
        "password": fields.String(
            required=True, description="Password for the new user"
        ),
    },
)

signup_output_dto = api.model(
    "SignupOutput",
    {
        "message": fields.String,
    },
)

token_output_dto = api.model(
    "TokenOutput",
    {
        "id": fields.Integer,
        "text": fields.String,
        "document_index": fields.Integer,
        "sentence_index": fields.Integer,
        "pos_tag": fields.String,
    },
)

token_output_list_dto = api.model(
    "TokenListOutput",
    {
        "tokens": fields.List(fields.Nested(token_output_dto)),
    },
)

login_input_dto = api.model(
    "LoginInput",
    {
        "email": fields.String(required=True, description="The email of the user"),
        "password": fields.String(
            required=True, description="The password of the user"
        ),
    },
)

login_output_dto = api.model(
    "LoginOutput",
    {
        "token": fields.String(
            required=True, description="The JWT token for authenticated user"
        ),
    },
)

mention_update_input_dto = api.model(
    "UpdateMentionInput",
    {
        "schema_mention_id": fields.Integer,
        "token_ids": fields.List(fields.Integer),
        "entity_id": fields.Integer,
    },
)

document_edit_output_soft_delete_dto = api.model(
    "DeleteDocumentEditOutput",
    {
        "message": fields.String,
    },
)

document_delete_output_dto = api.model(
    "DeleteDocumentOutput",
    {
        "message": fields.String,
    },
)

project_delete_output_model = api.model(
    "DeleteProjectOutput",
    {
        "message": fields.String,
    },
)

relation_update_input_dto = api.model(
    "UpdateRelationInput",
    {
        "schema_relation_id": fields.Integer,
        "isDirected": fields.Boolean,
        "mention_head_id": fields.Integer,
        "mention_tail_id": fields.Integer,
    },
)
