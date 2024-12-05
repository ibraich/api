from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.repositories.mention_repository import MentionRepository
from app.services.token_mention_service import TokenMentionService
from app.repositories.token_mention_repository import TokenMentionRepository
from app.dtos import mention_output_dto


class MentionService:
    def __init__(self, mention_repository, token_mention_service):
        self.__mention_repository = mention_repository
        self.token_mention_service = token_mention_service

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

    def create_mentions(self, data):
        mentions = self.__mention_repository.get_mention_by_tag(self, data["tag"])
        if len(mentions) > 1:
            raise Conflict("There are more than one mention for this tag.")

        mention = self.__mention_repository.create_mention(
            self,
            data["document_edit_id"],
            data["tag"],
            data["is_shown_recommendation"],
            data["document_recommendation_id"],
        )

        mention_output_dto()
        for token_id in data["token_ids"]:
            self.token_mention_service.create_token_mention(token_id, mention.id)

        return mention, 200


mention_service = MentionService(
    MentionRepository(), TokenMentionService(TokenMentionRepository())
)
