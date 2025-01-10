from app.models import DocumentEdit
from app.db import db, Session
from app.repositories.base_repository import BaseRepository


class DocumentEditRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def create_document_edit(self, document_id, user_id, schema_id):
        document_edit = DocumentEdit(
            document_id=document_id,
            user_id=user_id,
            schema_id=schema_id,
            state_id=1,
            active=True,
        )
        return super().store_object_transactional(document_edit)

    def get_document_edit_by_document(self, document_id, user_id):
        return (
            Session.query(DocumentEdit)
            .filter(DocumentEdit.document_id == document_id)
            .filter(DocumentEdit.user_id == user_id)
            .filter(DocumentEdit.active == True)
            .first()
        )
