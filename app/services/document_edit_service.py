from werkzeug.exceptions import BadRequest, NotFound

from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.document_recommendation_service import (
    DocumentRecommendationService,
    document_recommendation_service,
)
from app.services.schema_service import SchemaService, schema_service
from app.services.user_service import UserService, user_service
from app.services.token_service import TokenService, token_service
from app.services.mention_services import MentionService, mention_service
from app.services.relation_services import RelationService, relation_service


class DocumentEditService:
    __document_edit_repository: DocumentEditRepository
    user_service: UserService
    document_recommendation_service: DocumentRecommendationService
    token_service: TokenService
    mention_service: MentionService
    relation_service: RelationService
    schema_service: SchemaService

    def __init__(
        self,
        document_edit_repository: DocumentEditRepository,
        user_service: UserService,
        document_recommendation_service: DocumentRecommendationService,
        token_service: TokenService,
        mention_service: MentionService,
        relation_service: RelationService,
        schema_service: SchemaService,
    ):
        self.__document_edit_repository = document_edit_repository
        self.user_service = user_service
        self.document_recommendation_service = document_recommendation_service
        self.token_service = token_service
        self.mention_service = mention_service
        self.relation_service = relation_service
        self.schema_service = schema_service

    def create_document_edit(
        self,
        document_id,
        model_mention: None,
        model_entities: None,
        model_relation: None,
        model_settings_mention: None,
        model_settings_entities: None,
        model_settings_relation: None,
    ):
        user_id = self.user_service.get_logged_in_user_id()

        # Check if document edit already exists
        doc_edit = self.get_document_edit_by_document(document_id, user_id)
        if doc_edit is not None:
            raise BadRequest("Document Edit already exists")

        # Check if user has access to this document
        document = self.user_service.check_user_document_accessible(
            user_id, document_id
        )

        self.schema_service.check_models_in_schema(
            model_mention, model_entities, model_relation, document.schema_id
        )

        # Create document edit
        document_edit = self.__document_edit_repository.create_document_edit(
            document_id,
            user_id,
            document.schema_id,
            model_mention,
            model_entities,
            model_relation,
        )

        # Create document recommendation for document edit
        document_recommendation = (
            self.document_recommendation_service.create_document_recommendation(
                document_edit_id=document_edit.id, document_id=document_id
            )
        )

        # Store model settings
        self.__document_edit_repository.store_model_settings(
            document_edit.id, model_mention, model_settings_mention
        )
        self.__document_edit_repository.store_model_settings(
            document_edit.id, model_entities, model_settings_entities
        )
        self.__document_edit_repository.store_model_settings(
            document_edit.id, model_relation, model_settings_relation
        )

        # TODO: generate recommendations for document edit

        return {
            "id": document_edit.id,
            "schema_id": document_edit.schema_id,
            "document_id": document_edit.document_id,
            "mention_model_id": document_edit.mention_model_id,
            "entity_model_id": document_edit.entity_model_id,
            "relation_model_id": document_edit.relation_model_id,
        }

    def get_document_edit_by_document(self, document_id, user_id):
        return self.__document_edit_repository.get_document_edit_by_document(
            document_id, user_id
        )

    def overtake_document_edit(self, document_edit_id):

        document_edit = self.__document_edit_repository.get_document_edit_by_id(
            document_edit_id
        )

        if document_edit is None:
            raise BadRequest("Document edit does not exist")

        logged_in_user_id = self.user_service.get_logged_in_user_id()
        current_owner_id = document_edit.user_id

        if logged_in_user_id == current_owner_id:
            raise BadRequest("User already has access to this document edit")
        # check for team
        user_service.check_user_document_accessible(
            logged_in_user_id, document_edit.document_id
        )

        # check if another document edit exist for current user
        existing_document_edit = self.get_document_edit_by_document(
            document_edit.document_id, logged_in_user_id
        )
        if existing_document_edit is not None:
            raise BadRequest("Document edit already exists")

        document_edit.user_id = logged_in_user_id

        # save
        self.__document_edit_repository.store_object(document_edit)

        return {
            "id": document_edit.id,
            "schema_id": document_edit.schema_id,
            "document_id": document_edit.document_id,
            "mention_model_id": document_edit.mention_model_id,
            "entity_model_id": document_edit.entity_model_id,
            "relation_model_id": document_edit.relation_model_id,
        }

    def soft_delete_document_edit(self, document_edit_id):

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(user_id, document_edit_id)

        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. Must be a positive integer.")

        success = self.__document_edit_repository.soft_delete_document_edit(
            document_edit_id
        )
        if not success:
            raise NotFound("DocumentEdit not found or already inactive.")
        return {"message": "DocumentEdit set to inactive successfully."}

    def soft_delete_edits_for_document(self, document_id):
        self.__document_edit_repository.soft_delete_document_edits_by_document_id(
            document_id
        )

    def bulk_soft_delete_edits_for_documents(self, document_ids: list[int]):
        if not document_ids:
            return
        self.__document_edit_repository.bulk_soft_delete_edits(document_ids)

    def get_document_edit_by_id(self, document_edit_id):
        document_edit = self.__document_edit_repository.get_document_edit_by_id(
            document_edit_id
        )
        if document_edit is None:
            raise BadRequest("Document Edit doesnt exist")

        tokens_data = self.token_service.get_tokens_by_document(
            document_edit.document_id
        )
        tokens = tokens_data.get("tokens", [])
        mentions_data = self.mention_service.get_mentions_by_document_edit(
            document_edit_id
        )

        transformed_mentions = [
            {
                "tag": mention["tag"],
                "tokens": mention["tokens"],
                "entity": {"id": mention["entity_id"]},
            }
            for mention in mentions_data.get("mentions", [])
        ]
        relations_data = self.relation_service.get_relations_by_document_edit(
            document_edit_id
        )

        transformed_relations = [
            {
                "tag": relation["tag"],
                "head_mention": {
                    "tag": relation["head_mention"]["tag"],
                    "tokens": relation["head_mention"]["tokens"],
                    "entity": {"id": relation["head_mention"]["entity"]},
                },
                "tail_mention": {
                    "tag": relation["tail_mention"]["tag"],
                    "tokens": relation["tail_mention"]["tokens"],
                    "entity": {"id": relation["tail_mention"]["entity"]},
                },
            }
            for relation in relations_data.get("relations", [])
        ]
        return {
            "document": {
                "id": document_edit.document_id,
                "tokens": tokens,
            },
            "mentions": transformed_mentions,
            "relations": transformed_relations,
        }

    def get_document_edit_model(self, document_edit_id):
        settings = self.__document_edit_repository.get_document_edit_model(
            document_edit_id
        )
        model_dict = {}
        for setting in settings:
            if setting.id not in model_dict:
                model_dict[setting.id] = {
                    "document_edit_id": setting.document_edit_id,
                    "id": setting.id,
                    "name": setting.model_name,
                    "type": setting.model_type,
                    "step_id": setting.model_step_id,
                    "step_name": setting.model_step_name,
                    "settings": [],
                }
                model_dict[setting.id]["settings"].append(
                    {
                        "id": setting.settings_id,
                        "value": setting.value,
                        "name": setting.key,
                    }
                )
        return {"models": list(model_dict.values())}


document_edit_service = DocumentEditService(
    DocumentEditRepository(),
    user_service,
    document_recommendation_service,
    token_service,
    mention_service,
    relation_service,
    schema_service,
)
