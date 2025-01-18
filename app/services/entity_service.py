from app.models import Entity
from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from app.services.schema_service import schema_service
from app.services.user_service import UserService, user_service
from app.repositories.mention_repository import MentionRepository
import requests
import os

RECOMMENDATION_SYSTEM_URL = os.getenv("RECOMMENDATION_SYSTEM_URL", "http://localhost:8080/pipeline/docs")

class EntityService:
    def __init__(self, entity_repository, mention_repository, schema_service):
        self.__entity_repository = entity_repository
        self.__mention_repository = mention_repository
        self.schema_service = schema_service

    def get_entities_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        entities = self.__entity_repository.get_entities_by_document_edit(
            document_edit_id
        )
        if not entities:
            raise NotFound("No entities found for the given document edit.")

        entity_list = [
            {
                "id": entity.id,
                "isShownRecommendation": entity.isShownRecommendation,
                "document_edit_id": entity.document_edit_id,
                "document_recommendation_id": entity.document_recommendation_id,
            }
            for entity in entities
        ]
        return {"entities": entity_list}

    def create_in_edit(self, document_edit_id: int) -> Entity:
        return self.__entity_repository.create_in_edit(document_edit_id)

    def delete_entity(self, entity_id):
        entity = self.__entity_repository.get_entity_by_id(entity_id)
        if not entity:
            raise NotFound("Entity not found.")

        if entity.document_edit_id is None:
            raise BadRequest("Entity must belong to a valid document_edit_id.")

        # logged_in_user_id = user_service.get_logged_in_user_id()
        # document_edit_user_id = user_service.get_user_by_document_edit_id(entity.document_edit_id)

        # if logged_in_user_id != document_edit_user_id:
        # raise NotFound("The logged in user does not belong to this document.")

        mentions_updated = self.__mention_repository.set_entity_id_to_null(entity_id)
        if mentions_updated > 0:
            print(f"Updated {mentions_updated} mentions to set entity_id to NULL.")

        self.__entity_repository.delete_entity_by_id(entity_id)
        return {"message": "Entity deleted successfully."}

    def check_entity_in_document_edit(self, entity_id, document_edit_id):
        entity = self.__entity_repository.get_entity_by_id(entity_id)
        if not entity:
            raise BadRequest("Entity does not exist")
        if entity.document_edit_id != document_edit_id:
            raise Forbidden("Entity does not belong to this document")

    def create_entity(self, data):

        # check if user is allowed to access this document edit
        logged_in_user_id = user_service.get_logged_in_user_id()
        document_edit_user_id = user_service.get_user_by_document_edit_id(
            data["document_edit_id"]
        )

        if logged_in_user_id != document_edit_user_id:
            raise NotFound("The logged in user does not belong to this document.")

        mention_ids = data["mention_ids"]
        mentions = []

        schema = self.schema_service.get_schema_by_document_edit(
            data["document_edit_id"]
        )

        tag_count = dict()
        for mention_id in mention_ids:
            mention = self.__mention_repository.get_mention_by_id(mention_id)
            if mention is None:
                raise BadRequest("Invalid mention ids.")

            if mention.document_edit_id != data["document_edit_id"]:
                raise BadRequest("Invalid mention id")

            # Check that entity is allowed for mentions
            self.schema_service.verify_entity_possible(schema.id, mention.tag)

            # counting tags to check if all tags are same or not
            if mention.tag not in tag_count:
                tag_count[mention.tag] = 0
            else:
                tag_count[mention.tag] += 1
            mentions.append(mention)

        # if a mention does not exist already
        if len(mentions) != len(mention_ids):
            raise BadRequest("Invalid mention ids.")

        # if two or more tags exist in mention then throw error
        if len(tag_count) > 1:
            raise BadRequest("Mention with multiple types of tag detected")

        # save entity
        entity = self.__entity_repository.create_entity(data["document_edit_id"])

        # add entity id to mention or replace previous one
        for mention in mentions:
            mention.entity_id = entity.id

        # commiting db session to save changes
        self.__mention_repository.save_mention()

        response = {
            "id": entity.id,
            "isShownRecommendation": entity.isShownRecommendation,
            "document_edit_id": entity.document_edit_id,
            "document_recommendation_id": entity.document_recommendation_id,
        }

        return response
    def detect_entities(self, payload, model_type, model, temperature):
        """
        Handles logic for entity detection and forwards data to the external API.
        """
        if not payload.get("document_id"):
            raise BadRequest("document_id is required in the payload.")

        response = requests.post(
            RECOMMENDATION_SYSTEM_URL,
            json={
                "payload": payload,
                "model_type": model_type,
                "model": model,
                "temperature": temperature,
            }
        )
        if response.status_code != 200:
            raise BadRequest(f"Recommendation system error: {response.text}")

        return response.json()

    def get_entity_by_id(self, entity_id):
        response = requests.get(f"{RECOMMENDATION_SYSTEM_URL}/{entity_id}")
        if response.status_code == 404:
            raise NotFound(f"Entity with ID {entity_id} not found.")
        return response.json()

    def delete_entity(self, entity_id):
        response = requests.delete(f"{RECOMMENDATION_SYSTEM_URL}/{entity_id}")
        if response.status_code == 404:
            raise NotFound(f"Entity with ID {entity_id} not found.")
        return True

# Singleton instance
entity_service = EntityService()


entity_service = EntityService(EntityRepository(), MentionRepository(), schema_service)
