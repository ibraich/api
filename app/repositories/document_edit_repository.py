from app.models import DocumentEdit, DocumentEditState
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

    def get_document_edit_by_id(self, document_edit_id):
        return (
            db.session.query(
                DocumentEdit.id,
                DocumentEdit.document_id,
                DocumentEdit.schema_id,
                DocumentEdit.user_id,
                DocumentEditState.type.label("state"),
            )
            .filter(DocumentEdit.id == document_edit_id)
            .filter(DocumentEdit.active == True)
            .join(DocumentEditState, DocumentEditState.id == DocumentEdit.state_id)
        ).first()

    def soft_delete_document_edit(self, document_edit_id):
        document_edit = (
            self.db_session.query(DocumentEdit)
            .filter(DocumentEdit.id == document_edit_id, DocumentEdit.active == True)
            .first()
        )
        if not document_edit:
            return False
        document_edit.active = False
        self.db_session.commit()
        return True

    def soft_delete_document_edits_by_document_id(self, document_id: int):
        (
            self.db_session.query(DocumentEdit)
            .filter(
                DocumentEdit.document_id == document_id,
                DocumentEdit.active == True,
            )
            .update({DocumentEdit.active: False}, synchronize_session=False)
        )
        self.db_session.commit()

    def bulk_soft_delete_edits(self, document_ids: list[int]):
        if not document_ids:
            return

        self.db_session.query(DocumentEdit).filter(
            DocumentEdit.document_id.in_(document_ids), DocumentEdit.active == True
        ).update({DocumentEdit.active: False}, synchronize_session=False)
        self.db_session.commit()

    def get_state_id_by_name(self, state):
        return (
            Session.query(DocumentEditState)
            .filter(DocumentEditState.type == state)
            .first()
        )

    def get_state_name_by_id(self, state_id):
        return (
            Session.query(DocumentEditState)
            .filter(DocumentEditState.id == state_id)
            .first()
        )

    def update_state(self, document_edit_id, state_id):
        document_edit = (
            Session.query(DocumentEdit)
            .filter(DocumentEdit.id == document_edit_id)
            .first()
        )
        document_edit.state_id = state_id
        self.store_object_transactional(document_edit)
        return document_edit
