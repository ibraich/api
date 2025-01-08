from app.models import (
    Document,
    DocumentRecommendation,
    DocumentState,
    Project,
    DocumentEditState,
    DocumentEdit,
    Team,
    User,
    UserTeam,
)
from app.repositories.base_repository import BaseRepository
from sqlalchemy import exc, and_
from app.db import db
from werkzeug.exceptions import NotFound

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

    def get_documents_by_user(self, user_id):
        return (
            db.session.query(
                Document.id,
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Team.name.label("team_name"),
                Team.id.label("team_id"),
                DocumentEditState.type.label("document_edit_state"),
                DocumentEdit.id.label("document_edit_id"),
            )
            .select_from(User)
            .filter(User.id == user_id)
            .join(UserTeam, User.id == UserTeam.user_id)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Team.id == Project.team_id)
            .join(Document, Project.id == Document.project_id)
            .join(DocumentState, DocumentState.id == Document.state_id)
            .outerjoin(
                DocumentEdit,
                and_(
                    Document.id == DocumentEdit.document_id,
                    DocumentEdit.user_id == user_id,
                ),
            )
            .outerjoin(DocumentEditState, DocumentEditState.id == DocumentEdit.state_id)
        )
    def get_recommendation_by_id(self, recommendation_id):
        """Fetch a recommendation by its ID."""
        recommendation = db.session.query(DocumentRecommendation).filter(
            DocumentRecommendation.id == recommendation_id
        ).first()
        if not recommendation:
            raise NotFound("Recommendation not found")
        return recommendation

    def mark_recommendation_as_not_shown(self, recommendation_id):
        """Mark a recommendation as not shown."""
        recommendation = self.get_recommendation_by_id(recommendation_id)
        recommendation.is_shown = False
        db.session.commit()

    def copy_recommendation_to_edit(self, recommendation_id):
        """Copy recommendation details to a document edit."""
        recommendation = self.get_recommendation_by_id(recommendation_id)
        if recommendation.is_entity:
            raise ValueError("Cannot copy entity recommendations.")
        
        document_edit = DocumentEdit(
            document_id=recommendation.document_id,
            content=recommendation.content,
            created_by=recommendation.created_by,
        )
        db.session.add(document_edit)
        db.session.commit()
        return document_edit

