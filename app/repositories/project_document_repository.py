from app.db import db, Session
from app.models import Project, Document, Schema, DocumentRecommendation
from sqlalchemy import and_

from app.repositories.base_repository import BaseRepository


class ProjectDocumentRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session

    def get_project_by_id(self, project_id):
        return db.session.query(Project).filter(Project.id == project_id).first()

    def get_document_by_id(self, document_id):
        return (
            Session.query(
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Schema.name.label("schema_name"),
                Project.team_id,
                DocumentRecommendation.id.label("document_recommendation_id"),
            )
            .select_from(Document)
            .filter(Document.id == document_id)
            .filter(Document.active == True)
            .join(Project, Project.id == Document.project_id)
            .join(Schema, Schema.id == Project.schema_id)
            .outerjoin(
                DocumentRecommendation,
                and_(
                    Document.id == DocumentRecommendation.document_id,
                    DocumentRecommendation.document_edit_id is None,
                ),
            )
        ).first()