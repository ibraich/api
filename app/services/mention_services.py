from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.repositories.mention_repository import MentionRepository
from app.services.project_service import ProjectService, project_service
from app.services.user_service import UserService, user_service
from app.services.document_edit_service import (
    DocumentEditService,
    document_edit_service,
)
from app.services.token_mention_service import (
    token_mention_service,
    TokenMentionService,
)
from app.repositories import mention_repository, relation_repository


class MentionService:
    __mention_repository: MentionRepository
    token_mention_service: TokenMentionService
    user_service: UserService
    project_service: ProjectService
    document_edit_service: DocumentEditService

    def __init__(
        self,
        mention_repository,
        token_mention_service,
        user_service,
        project_service,
        document_edit_service,
    ):
        self.__mention_repository = mention_repository
        self.token_mention_service = token_mention_service
        self.user_service = user_service
        self.project_service = project_service
        self.document_edit_service = document_edit_service

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

        return {"mentions": mentions_list}

    def create_mentions(self, data):

        # check if user is allowed to access this document edit
        logged_in_user_id = user_service.get_logged_in_user_id()
        document_edit_user_id = document_edit_service.get_user_id(
            data["document_edit_id"]
        )

        if logged_in_user_id != document_edit_user_id:
            raise NotFound("The logged in user does not belong to this document.")

        # check duplicates
        mentions = self.__mention_repository.get_mentions_by_document_edit(
            data["document_edit_id"]
        )
        if len(mentions) > 0:

            token_ids = data["token_ids"]
            mention_ids = []
            for mention in mentions:
                mention_ids.append(mention.id)

            duplicate_token_mention = token_mention_service.get_token_mention(
                token_ids, mention_ids
            )

            if len(duplicate_token_mention) > 0:
                raise Conflict("Token mention already exists.")

        # save mention
        mention = self.__mention_repository.create_mention(
            data["document_edit_id"],
            data["tag"],
        )

        # save token mention
        for token_id in data["token_ids"]:
            self.token_mention_service.create_token_mention(token_id, mention.id)

        return mention
    

    def accept_mention(self, mention_id: int, user_id: int):
        mention = self.mention_repository.get_by_id(mention_id)
        if not mention:
            raise NotFound(f"Mention with id {mention_id} not found.")
        if mention.user_id != user_id:
            raise Conflict("Mention does not belong to the current user.")
        if not mention.is_shown_recommendation:
            raise BadRequest("Mention recommendation is not active.")

        new_mention = self.mention_repository.copy_to_document_edit(mention, user_id)
        self.mention_repository.set_is_shown_recommendation_false(mention_id)
        return new_mention

    def reject_mention(self, mention_id: int, user_id: int):
        mention = self.mention_repository.get_by_id(mention_id)
        if not mention:
            raise NotFound(f"Mention with id {mention_id} not found.")
        if mention.user_id != user_id:
            raise Conflict("Mention does not belong to the current user.")
        if not mention.is_shown_recommendation:
            raise BadRequest("Mention recommendation is not active.")

        self.mention_repository.set_is_shown_recommendation_false(mention_id)
    
    def accept_mention(session, mention_id, user_id):
      # Holen der Mention und Validierung
        mention = mention_repository.get_mention_by_id_and_user(session, mention_id, user_id)
        if not mention:
            raise ValueError("Mention not found or does not belong to the user.")
    
        if not mention.is_shown_recommendation:
            raise ValueError("Mention is not a valid recommendation.")
    
        # Erstellen der neuen Mention-Daten
        try:
         new_mention_data = {
            "text": mention.text,
            "start_offset": mention.start_offset,
            "end_offset": mention.end_offset,
            "document_id": mention.document_id,
            "is_shown_recommendation": False,
            "document_recommendation_id": None,
        }
        except AttributeError as e:
            raise ValueError(f"Missing required mention data: {e}")
    
        # Erstellen der neuen Mention in der Dokumentbearbeitung
        try:
            mention_repository.create_mention_in_edit(session, new_mention_data)
        except Exception as e:
            raise ValueError(f"Failed to create mention in edit: {e}")
    
         # Aktualisieren des Recommendation-Status
        try:
            mention_repository.update_is_shown_recommendation(session, mention_id, False)
        except Exception as e:
            raise ValueError(f"Failed to update recommendation status: {e}")
    
        return new_mention_data

    def reject_relation(session, relation_id, user_id):
        relation = relation_repository.get_relation_by_id_and_user(session, relation_id, user_id)
        if not relation or not relation.is_shown_recommendation:
            raise ValueError("Invalid or non-recommendation relation.")
        relation_repository.update_is_shown_recommendation(session, relation_id, False)
        return {"message": "Relation recommendation rejected."}

mention_service = MentionService(
    MentionRepository(),
    token_mention_service,
    user_service,
    project_service,
    document_edit_service,
)