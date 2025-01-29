from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from app.services.user_service import user_service, UserService
from app.repositories.mention_repository import MentionRepository


class EntityMentionService:
    __entity_repository: EntityRepository
    __mention_repository: MentionRepository
    user_service: UserService

    def __init__(self, entity_repository, mention_repository, user_service):
        self.__entity_repository = entity_repository
        self.__mention_repository = mention_repository
        self.user_service = user_service

    def check_entity_in_document_edit(self, entity_id, document_edit_id):
        entity = self.__entity_repository.get_entity_by_id(entity_id)
        if not entity:
            raise BadRequest("Entity does not exist")
        if entity.document_edit_id != document_edit_id:
            raise Forbidden("Entity does not belong to this document")

    def delete_entity(self, entity_id):
        mentions_updated = self.__mention_repository.set_entity_id_to_null(entity_id)
        if mentions_updated > 0:
            print(f"Updated {mentions_updated} mentions to set entity_id to NULL.")

        self.__entity_repository.delete_entity_by_id(entity_id)
        return {"message": "Entity deleted successfully."}


entity_mention_service = EntityMentionService(
    EntityRepository(), MentionRepository(), user_service
)
