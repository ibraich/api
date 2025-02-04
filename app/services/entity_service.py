from app.models import Entity
from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from app.services.entity_mention_service import (
    entity_mention_service,
    EntityMentionService,
)
from app.services.mention_services import MentionService, mention_service
from app.services.schema_service import schema_service, SchemaService
from app.services.user_service import UserService, user_service


class EntityService:
    __entity_repository: EntityRepository
    schema_service: SchemaService
    user_service: UserService
    entity_mention_service: EntityMentionService
    mention_service: MentionService

    def __init__(
        self,
        entity_repository,
        schema_service,
        user_service,
        entity_mention_service,
        mention_service,
    ):
        self.__entity_repository = entity_repository
        self.schema_service = schema_service
        self.user_service = user_service
        self.entity_mention_service = entity_mention_service
        self.mention_service = mention_service

    def get_entities_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        entities = self.__entity_repository.get_entities_by_document_edit(
            document_edit_id
        )

        mentions = self.mention_service.get_mentions_by_document_edit(document_edit_id)
        if not entities:
            raise NotFound("No entities found for the given document edit.")

        entity_list = [
            {
                "id": entity.id,
                "isShownRecommendation": entity.isShownRecommendation,
                "document_edit_id": entity.document_edit_id,
                "document_recommendation_id": entity.document_recommendation_id,
                "mentions": [
                    mention
                    for mention in mentions["mentions"]
                    if mention["entity_id"] == entity.id
                ],
            }
            for entity in entities
        ]
        return {"entities": entity_list}

    def create_in_edit(self, document_edit_id: int) -> Entity:
        return self.__entity_repository.create_in_edit(document_edit_id)

    def delete_entity(self, entity_id):
        return self.entity_mention_service.delete_entity(entity_id)

    def create_entity(self, document_edit_id, mention_ids):
        # Fetch all mentions of document
        mentions_of_edit = self.mention_service.get_mentions_by_document_edit(
            document_edit_id
        )

        # Filter mentions of entity
        mentions_of_entity = [
            mention
            for mention in mentions_of_edit["mentions"]
            if mention["id"] in mention_ids
        ]
        # Check if a mention does not exist already
        if len(mentions_of_entity) != len(mention_ids):
            raise BadRequest("Invalid mention ids.")

        tag_count = dict()
        for mention in mentions_of_entity:

            # Check that entity is allowed for mentions
            if not mention["schema_mention"]["entityPossible"]:
                raise BadRequest("Entity not allowed for this mention")

            # counting tags to check if all tags are same or not
            if mention["schema_mention"]["id"] not in tag_count:
                tag_count[mention["schema_mention"]["id"]] = 1
            else:
                tag_count[mention["schema_mention"]["id"]] += 1

        # if two or more tags exist in mention then throw error
        if len(tag_count) > 1:
            raise BadRequest("Mention with multiple types of tag detected")

        # save entity
        entity = self.__entity_repository.create_entity(document_edit_id)

        # add entity id to mention or replace previous one
        for mention in mentions_of_entity:
            self.mention_service.add_to_entity(entity.id, mention["id"])
            mention["entity_id"] = entity.id

        response = {
            "id": entity.id,
            "isShownRecommendation": entity.isShownRecommendation,
            "document_edit_id": entity.document_edit_id,
            "document_recommendation_id": entity.document_recommendation_id,
            "mentions": mentions_of_entity,
        }

        return response

    def create_entity_for_mentions(self, document_edit_id):
        mentions = self.mention_service.get_mentions_by_document_edit(document_edit_id)
        mentions_without_entity = []
        for mention in mentions["mentions"]:
            if (
                mention["entity_id"] is None
                and mention["schema_mention"]["entityPossible"] is True
            ):
                mentions_without_entity.append(mention)

        for mention in mentions_without_entity:
            entity = self.__entity_repository.create_entity(document_edit_id)
            self.mention_service.add_to_entity(entity.id, mention["id"])
            mention["entity_id"] = entity.id
        return mentions_without_entity

    def save_entity_in_edit(
        self, document_edit_id, mentions, document_recommendation_id
    ):
        entity = self.__entity_repository.create_entity(
            document_edit_id,
            document_recommendation_id=document_recommendation_id,
            is_shown_recommendation=True,
        )
        for mention in mentions:
            mention_service.add_to_entity(entity.id, mention["id"])


entity_service = EntityService(
    EntityRepository(),
    schema_service,
    user_service,
    entity_mention_service,
    mention_service,
)
