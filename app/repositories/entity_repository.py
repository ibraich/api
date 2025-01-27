from app.models import Entity
from app.repositories.base_repository import BaseRepository


class EntityRepository(BaseRepository):

    def create_entity(
        self,
        document_edit_id,
        document_recommendation_id=None,
        is_shown_recommendation=False,
    ):

        entity = Entity(
            document_edit_id=document_edit_id,
            document_recommendation_id=document_recommendation_id,
            isShownRecommendation=is_shown_recommendation,
        )
        self.store_object(entity)
        return entity

    def get_entities_by_document_edit(self, document_edit_id):
        return (
            self.get_session()
            .query(Entity)
            .filter(
                (Entity.document_edit_id == document_edit_id)
                & (
                    Entity.document_recommendation_id.is_(None)
                    | Entity.isShownRecommendation.is_(True)
                )
            )
            .all()
        )

    def create_in_edit(self, document_edit_id: int) -> Entity:
        return super().store_object(
            Entity(document_edit_id=document_edit_id, isShownRecommendation=True)
        )

    def delete_entity_by_id(self, entity_id):
        entity = self.get_entity_by_id(entity_id)
        if entity:
            self.get_session().delete(entity)

    def get_entity_by_id(self, entity_id):
        return self.get_session().query(Entity).filter_by(id=entity_id).first()
