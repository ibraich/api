from werkzeug.exceptions import BadRequest, NotFound

from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.document_recommendation_service import (
    DocumentRecommendationService,
    document_recommendation_service,
)
from app.services.entity_service import EntityService, entity_service
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
    entity_service: EntityService

    def __init__(
        self,
        document_edit_repository,
        user_service,
        document_recommendation_service,
        token_service,
        mention_service,
        relation_service,
        schema_service,
        entity_service,
    ):
        self.__document_edit_repository = document_edit_repository
        self.user_service = user_service
        self.document_recommendation_service = document_recommendation_service
        self.token_service = token_service
        self.mention_service = mention_service
        self.relation_service = relation_service
        self.schema_service = schema_service
        self.entity_service = entity_service

    def create_document_edit(
        self,
        user_id,
        document_id,
        model_mention=None,
        model_entities=None,
        model_relation=None,
        model_settings_mention=None,
        model_settings_entities=None,
        model_settings_relation=None,
    ):
        # Check if document edit already exists
        existing_doc_edit = self.get_document_edit_by_document(document_id, user_id)
        if existing_doc_edit is not None:
            raise BadRequest("Document Edit already exists")

        # Get schema of document
        schema = self.schema_service.get_schema_by_document(document_id)

        # Use default llm if no model is specified
        if not all([model_mention, model_relation, model_entities]):
            models = self.schema_service.get_models_by_schema(schema.id)
            models = [
                model
                for model in models
                if model["name"] == "OpenAI Large Language Model"
            ]
            if model_mention is None:
                for model in models:
                    if model["step"]["id"] == 1:
                        model_mention = model["id"]
            if model_entities is None:
                for model in models:
                    if model["step"]["id"] == 2:
                        model_entities = model["id"]
            if model_relation is None:
                for model in models:
                    if model["step"]["id"] == 3:
                        model_relation = model["id"]

        self.schema_service.check_models_in_schema(
            model_mention, model_entities, model_relation, schema.id
        )

        # Create document edit
        document_edit = self.__document_edit_repository.create_document_edit(
            document_id,
            user_id,
            schema.id,
            model_mention,
            model_entities,
            model_relation,
        )
        doc_edit = self.get_document_edit_with_document_by_id(document_edit.id)

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

        # Create mention recommendation
        params = self.get_recommendation_params(document_edit.id, 1)  # MENTIONS

        mention_recommendations = (
            self.document_recommendation_service.get_mention_recommendation(
                document_id, doc_edit.schema_id, doc_edit.content, params
            )
        )
        self.mention_service.create_recommended_mention(
            document_edit.id, document_recommendation.id, mention_recommendations
        )

        return {
            "id": document_edit.id,
            "schema_id": document_edit.schema_id,
            "document_id": document_edit.document_id,
            "mention_model_id": document_edit.mention_model_id,
            "entity_model_id": document_edit.entity_model_id,
            "relation_model_id": document_edit.relation_model_id,
            "state": {"id": 5, "state": "MENTION_SUGGESTION"},
        }

    def get_document_edit_by_document(self, document_id, user_id):
        return self.__document_edit_repository.get_document_edit_by_document(
            document_id, user_id
        )

    def get_document_edit_with_document_by_id(self, document_edit_id):
        return self.__document_edit_repository.get_document_edit_with_document_by_id(
            document_edit_id
        )

    def overtake_document_edit(self, logged_in_user_id, document_edit_id):
        document_edit = self.__document_edit_repository.get_document_edit_by_id(
            document_edit_id
        )
        if document_edit is None:
            raise BadRequest("Document edit does not exist")

        current_owner_id = document_edit.user_id

        if logged_in_user_id == current_owner_id:
            raise BadRequest("User already has access to this document edit")
        # check for team

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
            "state": {
                "id": document_edit.state_id,
                "state": document_edit.state_name,
            },
        }

    def soft_delete_document_edit(self, document_edit_id):
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
        relations_data = self.relation_service.get_relations_by_document_edit(
            document_edit_id
        )
        return {
            "document": {
                "id": document_edit.document_id,
                "tokens": tokens,
            },
            "schema_id": document_edit.schema_id,
            "mentions": mentions_data["mentions"],
            "relations": relations_data["relations"],
        }

    def get_document_edit_by_id_for_difference_calc(self, document_edit_id):
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

        non_recommended_mentions_dict = {
            mention["id"]: mention
            for mention in mentions_data.get("mentions", [])
            if mention["document_recommendation_id"] is None
        }

        transformed_mentions = [
            {
                "tag": mention["tag"],
                "tokens": mention["tokens"],
                **(
                    {"entity": {"id": mention["entity_id"]}}
                    if mention.get("entity_id")
                    else {}
                ),  # Only add entity object if entity_id exists
            }
            for mention in non_recommended_mentions_dict.get("mentions", [])
        ]
        relations_data = self.relation_service.get_relations_by_document_edit(
            document_edit_id
        )

        non_recommended_relations_dict = {
            relation["id"]: relation
            for relation in relations_data.get("relations", [])
            if relation["document_recommendation_id"] is None
        }

        transformed_relations = [
            {
                "tag": relation["tag"],
                "mention_head": {
                    "tag": relation["head_mention"]["tag"],
                    "tokens": relation["head_mention"]["tokens"],
                    **(
                        {"entity": {"id": relation["head_mention"]["entity_id"]}}
                        if relation["head_mention"].get("entity_id")
                        else {}
                    ),  # Only add entity object if entity_id exists
                    "entity": {"id": relation["head_mention"]["entity_id"]},
                },
                "mention_tail": {
                    "tag": relation["tail_mention"]["tag"],
                    "tokens": relation["tail_mention"]["tokens"],
                    **(
                        {"entity": {"id": relation["tail_mention"]["entity_id"]}}
                        if relation["tail_mention"].get("entity_id")
                        else {}
                    ),  # Only add entity object if entity_id exists
                },
            }
            for relation in non_recommended_relations_dict.get("relations", [])
        ]
        return {
            "document": {
                "id": document_edit.document_id,
                "tokens": tokens,
            },
            "schema_id": document_edit.schema_id,
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
                    "step": {
                        "id": setting.model_step_id,
                        "type": setting.model_step_name,
                    },
                    "settings": [],
                }

            if setting.settings_id is not None:
                model_dict[setting.id]["settings"].append(
                    {
                        "id": setting.settings_id,
                        "value": setting.value,
                        "key": setting.key,
                    }
                )
        return {"models": list(model_dict.values())}

    def save_relation_recommendation(self, document_edit_id):
        doc_edit = self.get_document_edit_with_document_by_id(document_edit_id)
        params = self.get_recommendation_params(document_edit_id, 2)  # RELATIONS
        self.document_recommendation_service.get_relation_recommendation(
            document_edit_id,
            doc_edit.schema_id,
            doc_edit.content,
            doc_edit.document_id,
            params,
        )

    def save_entity_recommendation(self, document_edit_id):
        doc_edit = self.get_document_edit_with_document_by_id(document_edit_id)
        params = self.get_recommendation_params(document_edit_id, 3)  # ENTITIES
        self.document_recommendation_service.get_entity_recommendation(
            document_edit_id,
            doc_edit.schema_id,
            doc_edit.content,
            doc_edit.document_id,
            params,
        )

    def get_recommendation_params(self, document_edit_id, step_id):
        params = {}
        models = self.get_document_edit_model(document_edit_id)["models"]
        for model in models:
            if model["step"]["id"] == step_id:
                params["model_type"] = model["type"]
                params["name"] = model["name"]
                for setting in model["settings"]:
                    params[setting["key"]] = setting["value"]
        return params

    def set_edit_state(self, document_edit_id, state_name):
        state = self.__document_edit_repository.get_state_by_name(state_name)
        if state is None:
            raise BadRequest("Invalid state")
        document_edit = self.__document_edit_repository.get_document_edit_by_id(
            document_edit_id
        )
        if document_edit is None:
            raise BadRequest("Document edit does not exist")

        if document_edit.state_name == "MENTION_SUGGESTION":
            if state_name != "MENTIONS":
                raise BadRequest("Not allowed to proceed to this step")
            recs = self.mention_service.get_recommendations_by_document_edit(
                document_edit_id
            )
            if len(recs) != 0:
                raise BadRequest("Unreviewed recommendations left")
        elif document_edit.state_name == "MENTIONS":
            if state_name != "ENTITIES":
                raise BadRequest("Not allowed to proceed to this step")

            self.save_entity_recommendation(document_edit_id)
            self.entity_service.create_entity_for_mentions(document_edit_id)

        elif document_edit.state_name == "ENTITIES":
            if state_name != "RELATION_SUGGESTION":
                raise BadRequest("Not allowed to proceed to this step")

            self.save_relation_recommendation(document_edit_id)

        elif document_edit.state_name == "RELATION_SUGGESTION":
            if state_name != "RELATIONS":
                raise BadRequest("Not allowed to proceed to this step")
            recs = self.relation_service.get_recommendations_by_document_edit(
                document_edit_id
            )
            if len(recs) != 0:
                raise BadRequest("Unreviewed recommendations left")
        elif document_edit.state_name == "RELATIONS":
            if state_name != "FINISHED":
                raise BadRequest("Not allowed to proceed to this step")
        elif document_edit.state_name == "FINISHED":
            raise BadRequest("Annotation already finished")
        else:
            raise BadRequest("Invalid state")
        document_edit = self.__document_edit_repository.update_state(
            document_edit_id, state.id
        )
        return {
            "id": document_edit.id,
            "schema_id": document_edit.schema_id,
            "document_id": document_edit.document_id,
            "mention_model_id": document_edit.mention_model_id,
            "entity_model_id": document_edit.entity_model_id,
            "relation_model_id": document_edit.relation_model_id,
            "state": {
                "id": state.id,
                "state": state.type,
            },
        }


document_edit_service = DocumentEditService(
    DocumentEditRepository(),
    user_service,
    document_recommendation_service,
    token_service,
    mention_service,
    relation_service,
    schema_service,
    entity_service,
)
