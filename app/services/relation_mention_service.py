from werkzeug.exceptions import BadRequest, NotFound

from app.repositories.relation_repository import RelationRepository


class RelationMentionService:

    __relation_repository: RelationRepository

    def __init__(
        self,
        relation_repository,
    ):
        self.__relation_repository = relation_repository

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

        # Proceed with deletion
        deleted = self.__relation_repository.delete_relation_by_id(relation_id)
        if not deleted:
            raise NotFound("Relation not found during deletion.")

        return {"message": "OK"}

    def get_relations_by_mention(self, mention_id):
        """
        Fetches relations where mention is part of.
        :param mention_id: Mention ID to query
        :return: List of relations
        """
        return self.__relation_repository.get_relations_by_mention(mention_id)


relation_mention_service = RelationMentionService(
    RelationRepository(),
)
