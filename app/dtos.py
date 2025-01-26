from flask_restx import fields
from app.extension import api

user_output_dto = api.model(
    "UserOutput",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
    },
)

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
        "entityPossible": fields.Boolean,
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
        "creator": fields.Nested(user_output_dto),
        "team_id": fields.Integer,
        "schema_id": fields.Integer,
    },
)

team_dto = api.model(
    "Team",
    {
        "id": fields.Integer,
        "name": fields.String,
    },
)

schema_dto = api.model(
    "Schema",
    {
        "id": fields.Integer,
        "name": fields.String,
    },
)

project_dto = api.model(
    "Project",
    {
        "id": fields.Integer,
        "name": fields.String,
    },
)

document_edit_dto = api.model(
    "DocumentEdit",
    {
        "id": fields.Integer,
        "state": fields.String,
    },
)

document_list_dto = api.model(
    "DocumentList",
    {
        "id": fields.Integer,
        "content": fields.String,
        "name": fields.String,
        "state": fields.Nested(
            api.model(
                "DocumentState",
                {
                    "id": fields.Integer,
                    "type": fields.String,
                },
            )
        ),
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
        "creator": fields.Nested(user_output_dto),
        "project_id": fields.Integer,
        "state_id": fields.Integer,
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
    },
)

team_input_dto = api.model(
    "TeamInput",
    {
        "name": fields.String(required=True),
    },
)

team_user_output_dto = api.model(
    "TeamUserOutput",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator": fields.Nested(user_output_dto),
        "members": fields.List(fields.Nested(user_output_dto)),
    },
)

document_edit_input_dto = api.model(
    "DocumentInput",
    {
        "document_id": fields.Integer(required=True, min=1),
    },
)

document_overtake_dto = api.model(
    "DocumentOvertake",
    {
        "document_edit_id": fields.Integer(required=True, min=1),
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


project_list_dto = api.model(
    "project_list_dto",
    {
        "id": fields.Integer,
        "name": fields.String,
        "creator": fields.Nested(user_output_dto),
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

token_model = api.model(
    "Token",
    {
        "id": fields.Integer(description="Token ID"),
        "text": fields.String(description="Token text"),
        "document_index": fields.Integer(
            description="Index of the token in the document"
        ),
        "sentence_index": fields.Integer(
            description="Index of the token in the sentence"
        ),
        "pos_tag": fields.String(description="Part-of-speech tag"),
    },
)

token_output_list_dto = api.model(
    "TokenListOutput",
    {
        "tokens": fields.List(fields.Nested(token_model)),
    },
)

entity_model = api.model(
    "Entity",
    {
        "id": fields.Integer(description="Entity ID"),
    },
)

mention_model = api.model(
    "Mention",
    {
        "tag": fields.String(description="Mention tag"),
        "tokens": fields.List(
            fields.Nested(token_model),
            description="List of tokens associated with the mention",
        ),
        "entity": fields.Nested(
            entity_model, description="Entity associated with the mention"
        ),
    },
)


head_mention_model = mention_model
tail_mention_model = mention_model

relation_model = api.model(
    "Relation",
    {
        "tag": fields.String(description="Relation tag"),
        "head_mention": fields.Nested(
            head_mention_model, description="Head mention in the relation"
        ),
        "tail_mention": fields.Nested(
            tail_mention_model, description="Tail mention in the relation"
        ),
    },
)

document_model = api.model(
    "Document",
    {
        "id": fields.Integer(description="Document ID"),
        "tokens": fields.List(
            fields.Nested(token_model), description="List of tokens in the document"
        ),
    },
)

finished_document_edit_output_dto = api.model(
    "DocumentEditOutput",
    {
        "document": fields.Nested(document_model, description="Document details"),
        "mentions": fields.List(
            fields.Nested(mention_model),
            description="List of mentions in the document edit",
        ),
        "relations": fields.List(
            fields.Nested(relation_model),
            description="List of relations in the document edit",
        ),
    },
)

mention_output_dto = api.model(
    "Mention",
    {
        "id": fields.Integer(description="Mention ID"),
        "tag": fields.String(description="Mention tag"),
        "isShownRecommendation": fields.Boolean(
            description="Whether the mention is shown as a recommendation"
        ),
        "document_edit_id": fields.Integer(description="Document Edit ID"),
        "document_recommendation_id": fields.Integer(
            description="Document Recommendation ID", nullable=True
        ),
        "entity_id": fields.Integer(
            description="Entity ID associated with the mention"
        ),
        "tokens": fields.List(
            fields.Nested(token_model),
            description="List of tokens associated with the mention",
        ),
        "schema_mention": fields.Nested(
            schema_mention_output_dto, description="Details of the schema mention"
        ),
    },
)

mention_output_list_dto = api.model(
    "MentionOutputList",
    {
        "mentions": fields.List(
            fields.Nested(mention_output_dto), description="List of mentions"
        ),
    },
)

schema_relation_model = api.model(
    "SchemaRelation",
    {
        "id": fields.Integer(description="Schema Relation ID"),
        "tag": fields.String(description="Schema Relation Tag"),
        "description": fields.String(description="Description of the schema relation"),
        "schema_id": fields.Integer(description="Schema ID"),
    },
)

mention_relation_model = api.model(
    "MentionRelation",
    {
        "tag": fields.String(description="Mention tag"),
        "tokens": fields.List(
            fields.Nested(token_model), description="List of tokens in the mention"
        ),
        "entity": fields.Integer(description="Entity ID associated with the mention"),
    },
)

relation_output_model = api.model(
    "RelationOutput",
    {
        "id": fields.Integer(description="Relation ID"),
        "isDirected": fields.Boolean(description="Whether the relation is directed"),
        "isShownRecommendation": fields.Boolean(
            description="Whether the relation is shown as a recommendation"
        ),
        "document_edit_id": fields.Integer(description="Document Edit ID"),
        "document_recommendation_id": fields.Integer(
            description="Document Recommendation ID", nullable=True
        ),
        "schema_relation": fields.Nested(
            schema_relation_model, description="Schema relation details"
        ),
        "tag": fields.String(description="Relation tag"),
        "head_mention": fields.Nested(
            mention_relation_model, description="Head mention of the relation"
        ),
        "tail_mention": fields.Nested(
            mention_relation_model, description="Tail mention of the relation"
        ),
    },
)

relation_output_list_dto = api.model(
    "RelationsOutput",
    {
        "relations": fields.List(
            fields.Nested(relation_output_model), description="List of relations"
        ),
    },
)
