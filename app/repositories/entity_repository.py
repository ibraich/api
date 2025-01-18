from app.models import Entity
from app.db import db
from app.repositories.base_repository import BaseRepository
import os

RECOMMENDATION_SYSTEM_URL = os.getenv("RECOMMENDATION_SYSTEM_URL", "http://localhost:8080/pipeline/docs")

class EntityRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session

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
    

    def get_document_by_id(self, document_id):
        # Simulate a database query
        return {"id": document_id, "content": "Sample document content"} if document_id == 1 else None

    def save_detected_entities(self, document_id, entities):
        # Simulate saving detected entities to the database
        return {"document_id": document_id, "entities_saved": len(entities)}
