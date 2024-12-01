from werkzeug.exceptions import BadRequest, NotFound

from app.repositories.mention_repository import MentionRepository


class MentionService:
    def __init__(self, mention_repository):
        self.__mention_repository = mention_repository

    def get_mentions_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        mentions = self.__mention_repository.get_mentions_by_document_edit(
            document_edit_id
        )

        if not mentions:
            raise NotFound("No mentions found for the given document edit.")

        # Serialize mentions to JSON-compatible format
        mentions_list = [
            {
                "id": mention.id,
                "tag": mention.tag,
                "isShownRecommendation": mention.isShownRecommendation,
                "document_edit_id": mention.document_edit_id,
                "document_recommendation_id": mention.document_recommendation_id,
                "entity_id": mention.entity_id,
            }
            for mention in mentions
        ]

        return {"mentions": mentions_list}, 200


mention_service = MentionService(MentionRepository())
