from app.models import Entity
from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import BadRequest, NotFound
from app.services.user_service import UserService, user_service
from app.repositories.mention_repository import MentionRepository


class EntityService:
    def __init__(self, entity_repository, mention_repository):
        self.__entity_repository = entity_repository
        self.__mention_repository = mention_repository

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


entity_service = EntityService(EntityRepository(), MentionRepository())
