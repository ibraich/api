
from app.models import Entity
from app.db import db

class EntityRepository:
    def __init__(self):
        self.db_session = db.session

    def get_entities_by_document_edit(self, document_edit_id):
        return (
            self.db_session.query(Entity)
            .filter_by(document_edit_id=document_edit_id)
            .all()
        )