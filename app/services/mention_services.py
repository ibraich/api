from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound, Conflict, Unauthorized

from app.repositories.mention_repository import MentionRepository
from app.services.project_service import ProjectService, project_service
from app.services.user_service import UserService, user_service
from app.services.relation_services import RelationService, relation_service
from app.services.entity_service import EntityService, entity_service

from app.services.token_mention_service import (
    token_mention_service,
    TokenMentionService,
)


class MentionService:
    __mention_repository: MentionRepository
    token_mention_service: TokenMentionService
    user_service: UserService
    project_service: ProjectService
    relation_service: RelationService
    entity_service: EntityService

    def __init__(
        self,
        mention_repository,
        token_mention_service,
        user_service,
        project_service,
        relation_service,
        entity_service,
    ):
        self.__mention_repository = mention_repository
        self.token_mention_service = token_mention_service
        self.user_service = user_service
        self.project_service = project_service
        self.relation_service = relation_service
        self.entity_service = entity_service

    def get_mentions_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        user_id = user_service.get_user_by_document_edit_id(document_edit_id)
        current_user_id = get_jwt_identity()

        if current_user_id != str(user_id):
            raise Unauthorized("You are not authorized to perform this action.")

        results = self.__mention_repository.get_mentions_with_tokens_by_document_edit(document_edit_id)

        mentions_dict = {}
        for row in results:
            if row.mention_id not in mentions_dict:
                mentions_dict[row.mention_id] = {
                    "id": row.mention_id,
                    "tag": row.tag,
                    "isShownRecommendation": row.isShownRecommendation,
                    "document_edit_id": row.document_edit_id,
                    "document_recommendation_id": row.document_recommendation_id,
                    "entity_id": row.entity_id,
                    "tokens": [],
                }
            if row.token_id is not None:
                mentions_dict[row.mention_id]["tokens"].append(row.token_id)

        return {"mentions": list(mentions_dict.values())}

    def create_mentions(self, data):

        # check if user is allowed to access this document edit
        logged_in_user_id = user_service.get_logged_in_user_id()
        document_edit_user_id = user_service.get_user_by_document_edit_id(
            data["document_edit_id"]
        )

        if logged_in_user_id != document_edit_user_id:
            raise NotFound("The logged in user does not belong to this document.")

        # check duplicates
        mentions = self.__mention_repository.get_mentions_with_tokens_by_document_edit(
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
            document_edit_id=data["document_edit_id"],
            tag=data["tag"],
        )

        # save token mention
        for token_id in data["token_ids"]:
            self.token_mention_service.create_token_mention(token_id, mention.id)

        return mention

    def copy_mention_recommendations_to_document_edit(
        self,
        document_recommendation_id_source,
        document_edit_id_target,
        document_recommendation_id_target,
    ):
        if document_recommendation_id_source is None:
            return

        mentions = self.__mention_repository.get_mentions_by_document_recommendation(
            document_recommendation_id_source
        )
        if mentions:
            for mention in mentions:
                self.__mention_repository.create_mention(
                    mention.tag,
                    document_edit_id=document_edit_id_target,
                    document_recommendation_id=document_recommendation_id_target,
                    is_shown_recommendation=True,
                )

    def delete_mention(self, mention_id):
        if not isinstance(mention_id, int) or mention_id <= 0:
            raise BadRequest("Invalid mention ID. It must be a positive integer.")

        mention = self.__mention_repository.get_mention_by_id(mention_id)
        if not mention:
            raise NotFound("Mention not found.")

        if mention.document_edit_id is None:
            raise BadRequest(
                "Cannot delete a mention without a valid document_edit_id."
            )

        # logged_in_user_id = user_service.get_logged_in_user_id()
        # document_edit_user_id = user_service.get_user_by_document_edit_id(mention.document_edit_id)

        # if logged_in_user_id != document_edit_user_id:
        # raise NotFound("The logged in user does not belong to this document.")

        related_relations = self.relation_service.get_relations_by_mention(mention_id)
        for relation in related_relations:
            self.relation_service.delete_relation_by_id(relation.id)

        self.token_mention_service.delete_token_mentions_by_mention_id(mention_id)

        if mention.entity_id is not None:
            mentions_with_entity = self.__mention_repository.get_mentions_by_entity_id(
                mention.entity_id
            )

            if (
                len(mentions_with_entity) == 1
                and mentions_with_entity[0].id == mention_id
            ):
                self.entity_service.delete_entity(mention.entity_id)

        deleted = self.__mention_repository.delete_mention_by_id(mention_id)
        if not deleted:
            raise NotFound("Mention not found during deletion.")

        return {"message": "OK"}


mention_service = MentionService(
    MentionRepository(),
    token_mention_service,
    user_service,
    project_service,
    relation_service,
    entity_service,
)
