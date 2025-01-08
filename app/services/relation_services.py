from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.repositories.relation_repository import RelationRepository


class RelationService:
    def __init__(self, relation_repository, document_edit_service):
        self.__relation_repository = relation_repository
        self.document_edit_service = document_edit_service

    def get_relations_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        relations = self.__relation_repository.get_relations_by_document_edit(
            document_edit_id
        )

        if not relations:
            raise NotFound("No relations found for the given document edit.")

        # Serialize mentions to JSON-compatible format
        relation_list = [
            {
                "id": relation.id,
                "tag": relation.tag,
                "isShownRecommendation": relation.isShownRecommendation,
                "isDirected": relation.isDirected,
                "mention_head_id": relation.mention_head_id,
                "mention_tail_id": relation.mention_tail_id,
            }
            for relation in relations
        ]

        return {"relations": relation_list}
    
    def accept_relation(self, relation_id: int, user_id: int):
        relation = self.relation_repository.get_by_id(relation_id)
        if not relation:
            raise NotFound(f"Relation with id {relation_id} not found.")
        if relation.user_id != user_id:
            raise Conflict("Relation does not belong to the current user.")
        if not relation.is_shown_recommendation:
            raise BadRequest("Relation recommendation is not active.")

        new_relation = self.relation_repository.copy_to_document_edit(relation, user_id)
        self.relation_repository.set_is_shown_recommendation_false(relation_id)
        return new_relation

    def reject_relation(self, relation_id: int, user_id: int):
        relation = self.relation_repository.get_by_id(relation_id)
        if not relation:
            raise NotFound(f"Relation with id {relation_id} not found.")
        if relation.user_id != user_id:
            raise Conflict("Relation does not belong to the current user.")
        if not relation.is_shown_recommendation:
            raise BadRequest("Relation recommendation is not active.")

        self.relation_repository.set_is_shown_recommendation_false(relation_id)


relation_service = RelationService(RelationRepository())
