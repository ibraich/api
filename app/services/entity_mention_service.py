from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import NotFound, Forbidden
from app.repositories.mention_repository import MentionRepository


class EntityMentionService:
    __entity_repository: EntityRepository
    __mention_repository: MentionRepository

    def __init__(self, entity_repository, mention_repository):
        self.__entity_repository = entity_repository
        self.__mention_repository = mention_repository

    def check_entity_in_document_edit(self, entity_id, document_edit_id):
        """
        Check if an entity belongs to a documentEdit.

        :param entity_id: Entity ID to check
        :param document_edit_id: DocumentEdit ID to check
        :raises NotFound: If entity does not exist.
        :raises Forbidden: If entity does not belong to the document.
        """
        entity = self.__entity_repository.get_entity_by_id(entity_id)
        if not entity:
            raise NotFound("Entity does not exist")
        if entity.document_edit_id != document_edit_id:
            raise Forbidden("Entity does not belong to this document")

    def delete_entity(self, entity_id):
        """
        Delete an entity by its ID.
        Sets entity ID of all mentions that are part of this entity to NULL.
        :param entity_id: Entity ID to delete.
        :return: Success message
        """
        self.__mention_repository.set_entity_id_to_null(entity_id)

        self.__entity_repository.delete_entity_by_id(entity_id)
        return {"message": "Entity deleted successfully."}


entity_mention_service = EntityMentionService(EntityRepository(), MentionRepository())
