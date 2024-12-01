from werkzeug.exceptions import BadRequest, NotFound

from app.repositories.relation_repository import RelationRepository


class RelationService:
    def __init__(self, relation_repository):
        self.__relation_repository = relation_repository

    def get_relations_by_document(self, document_id):
        if not isinstance(document_id, int) or document_id <= 0:
            raise BadRequest("Invalid document ID. It must be a positive integer.")

        relations = self.__relation_repository.get_relations_by_document(document_id)

        if not relations:
            raise NotFound("No relations found for the given document.")

        # Serialize mentions to JSON-compatible format
        relation_list = [
            {
                "id": relation.id,
                "tag": relation.tag,
                "isShownRecommendation": relation.isShownRecommendation,
                "isDirected":relation.isDirected,
                "mention_head_id": relation.mention_head_id,
                "mention_tail_id": relation.mention_tail_id,
            }
            for relation in relations
        ]

        return {"relations": relation_list}, 200
relation_service = RelationService(RelationRepository)