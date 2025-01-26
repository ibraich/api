from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.models import Relation
from app.repositories.relation_repository import RelationRepository
from app.services.schema_service import schema_service
from app.services.user_service import user_service
from app.services.mention_services import mention_service


class RelationMentionService:
    def __init__(
        self,
        relation_repository,
        user_service,
    ):
        self.__relation_repository = relation_repository
        self.user_service = user_service

    def delete_relation_by_id(self, relation_id):
        if not isinstance(relation_id, int) or relation_id <= 0:
            raise BadRequest("Invalid relation ID. It must be a positive integer.")

        # Fetch the relation to perform validation
        relation = self.__relation_repository.get_relation_by_id(relation_id)
        if not relation:
            raise NotFound("Relation not found.")

        # Check if document_edit_id is null
        if relation.document_edit_id is None:
            raise BadRequest(
                "Cannot delete a relation without a valid document_edit_id."
            )

        user_id = user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(
            user_id, relation.document_edit_id
        )

        # Proceed with deletion
        deleted = self.__relation_repository.delete_relation_by_id(relation_id)
        if not deleted:
            raise NotFound("Relation not found during deletion.")

        return {"message": "OK"}

    def get_relations_by_mention(self, mention_id):
        return self.__relation_repository.get_relations_by_mention(mention_id)


relation_mention_service = RelationMentionService(
    RelationRepository(),
    user_service,
)
