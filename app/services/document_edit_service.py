from werkzeug.exceptions import BadRequest, NotFound, Forbidden, InternalServerError

from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.document_recommendation_service import (
    DocumentRecommendationService,
    document_recommendation_service,
)
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

    def __init__(
        self,
        document_edit_repository: DocumentEditRepository,
        user_service: UserService,
        document_recommendation_service: DocumentRecommendationService,
        token_service: TokenService,
        mention_service: MentionService,
        relation_service: RelationService,
    ):
        self.__document_edit_repository = document_edit_repository
        self.user_service = user_service
        self.document_recommendation_service = document_recommendation_service
        self.token_service = token_service
        self.mention_service = mention_service
        self.relation_service = relation_service

    def create_document_edit(self, document_id):
        user_id = self.user_service.get_logged_in_user_id()

        # Check if document edit already exists
        doc_edit = self.get_document_edit_by_document(document_id, user_id)
        if doc_edit is not None:
            raise BadRequest("Document Edit already exists")

        # Check if user has access to this document
        document = self.user_service.check_user_document_accessible(
            user_id, document_id
        )

        # Create document edit
        document_edit = self.__document_edit_repository.create_document_edit(
            document_id, user_id, document.schema_id
        )

        # Create document recommendation for document edit
        document_recommendation = (
            self.document_recommendation_service.create_document_recommendation(
                document_edit_id=document_edit.id, document_id=document_id
            )
        )

        # Copy mention recommendations from document to new document edit
        self.document_recommendation_service.copy_document_recommendations(
            document.document_recommendation_id,
            document_edit.id,
            document_recommendation.id,
        )
        return {
            "id": document_edit.id,
            "schema_id": document_edit.schema_id,
            "document_id": document_edit.document_id,
            "state": "MENTION_SUGGESTION",
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
            "state": document_edit.state,
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

    def set_edit_state(self, document_edit_id, state_name):
        state = self.__document_edit_repository.get_state_id_by_name(state_name)
        if state is None:
            raise BadRequest("Invalid state")

        document_edit = self.__document_edit_repository.get_document_edit_by_id(
            document_edit_id
        )
        if document_edit is None:
            raise BadRequest("Document edit does not exist")

        user_id = self.user_service.get_logged_in_user_id()
        if document_edit.user_id != user_id:
            raise Forbidden("You are not allowed to edit this document")

        if document_edit.state == "MENTION_SUGGESTION":
            if state_name != "MENTIONS":
                raise BadRequest("Not allowed to proceed to this step")

            recs = self.mention_service.get_recommendations_by_document_edit(
                document_edit_id
            )
            if len(recs) != 0:
                raise BadRequest("Unreviewed recommendations left")

        elif document_edit.state == "MENTIONS":
            if state_name != "ENTITIES":
                raise BadRequest("Not allowed to proceed to this step")

            # TODO: Trigger Entity Recommendation Generation

        elif document_edit.state == "ENTITIES":
            if state_name != "RELATION_SUGGESTION":
                raise BadRequest("Not allowed to proceed to this step")

            # TODO: Trigger Relation Recommendation Generation

        elif document_edit.state == "RELATION_SUGGESTION":
            if state_name != "RELATIONS":
                raise BadRequest("Not allowed to proceed to this step")

            recs = self.relation_service.get_recommendations_by_document_edit(
                document_edit_id
            )
            if len(recs) != 0:
                raise BadRequest("Unreviewed recommendations left")

        elif document_edit.state == "RELATIONS":
            if state_name != "FINISHED":
                raise BadRequest("Not allowed to proceed to this step")

        elif document_edit.state == "FINISHED":
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
            "state": self.__document_edit_repository.get_state_name_by_id(
                document_edit.state_id
            ).type,
        }


document_edit_service = DocumentEditService(
    DocumentEditRepository(),
    user_service,
    document_recommendation_service,
    token_service,
    mention_service,
    relation_service,
)
