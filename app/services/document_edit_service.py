from werkzeug.exceptions import BadRequest, NotFound

from app.models import DocumentEdit
from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.document_recommendation_service import (
    DocumentRecommendationService,
    document_recommendation_service,
)


from app.services.entity_service import EntityService, entity_service
from app.services.mention_services import MentionService, mention_service
from app.services.relation_services import RelationService, relation_service
from app.services.token_service import TokenService, token_service

from app.services.user_service import UserService, user_service


class DocumentEditService:
    __document_edit_repository: DocumentEditRepository
    user_service: UserService
    document_recommendation_service: DocumentRecommendationService
    token_service: TokenService
    mention_service: MentionService
    relation_service: RelationService
    entity_service: EntityService

    def __init__(
        self,
        document_edit_repository: DocumentEditRepository,
        user_service: UserService,
        document_recommendation_service: DocumentRecommendationService,
        token_service: TokenService,
        mention_service: MentionService,
        relation_service: RelationService,
        entity_service: EntityService,
    ):
        self.__document_edit_repository = document_edit_repository
        self.user_service = user_service
        self.document_recommendation_service = document_recommendation_service
        self.token_service = token_service
        self.mention_service = mention_service
        self.relation_service = relation_service
        self.entity_service = entity_service

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
        }

    def get_by_id(self, document_edit_id) -> DocumentEdit:
        document_edit: DocumentEdit = self.__document_edit_repository.get_by_id(
            document_edit_id
        )
        mentions = self.mention_service.get_by_document_edit(document_edit_id)
        tokens = self.token_service.get_tokens_by_document(document_edit.document_id)
        for mention in mentions:
            print(mention, flush=True)
        relations = self.relation_service.get_by_document_edit(document_edit_id)
        document_edit.document.tokens = tokens
        document_edit.mentions = mentions
        document_edit.relations = relations

        # service still returns business model object
        # controller is responsible to return json valid format
        return document_edit

    def get_document_edit_by_document(self, document_id, user_id):
        return self.__document_edit_repository.get_document_edit_by_document(
            document_id, user_id
        )

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


document_edit_service = DocumentEditService(
    DocumentEditRepository(),
    user_service,
    document_recommendation_service,
    token_service,
    mention_service,
    relation_service,
    entity_service,
)
