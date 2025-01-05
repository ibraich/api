from app.models import Entity
from app.db import db
from app.repositories.base_repository import BaseRepository


class EntityRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session

    def get_entities_by_document_edit(self, document_edit_id):
        return (
            self.db_session.query(Entity)
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
        return super().store_object_transactional(
            Entity(document_edit_id=document_edit_id, isShownRecommendation=True)
        )

    def delete_entity_by_id(self, entity_id):
        entity = self.get_entity_by_id(entity_id)
        if entity:
            self.db_session.delete(entity)
            self.db_session.commit()

    def get_entity_by_id(self, entity_id):
        return self.db_session.query(Entity).filter_by(id=entity_id).first()
