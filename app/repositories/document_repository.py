from app.models import Document, DocumentState, Project, DocumentEditState, DocumentEdit
from app.repositories.base_repository import BaseRepository
from sqlalchemy import exc
from app.db import db


class DocumentRepository(BaseRepository):
    def get_documents_by_project(self, project_id):
        return (
            db.session.query(
                Document.id,
                Document.content,
                Document.name,
                Document.project_id,
                DocumentState.type,
                Project.name.label("project_name"),
            )
            .join(Project)
            .join(DocumentState)
            .filter(Document.project_id == project_id)
        ).all()

    def get_document_edit_by_user_and_document(self, user_id, document_id):
        return (
            db.session.query(
                DocumentEditState.type.label("document_edit_type"),
                DocumentEdit.id.label("document_edit_id"),
            )
            .filter(
                DocumentEdit.document_id == document_id, DocumentEdit.user_id == user_id
            )
            .join(DocumentEditState)
            .first()
        )
