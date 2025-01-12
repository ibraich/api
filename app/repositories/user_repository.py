from sqlalchemy import and_
from werkzeug.exceptions import NotFound

from app.models import (
    UserTeam,
    DocumentEdit,
    User,
    Team,
    Project,
    Document,
    Schema,
    DocumentRecommendation,
)
from app.repositories.base_repository import BaseRepository
from app.db import db, Session


class UserRepository(BaseRepository):
    def check_user_in_team(self, user_id, team_id):
        return (
            Session.query(UserTeam)
            .filter(UserTeam.user_id == user_id, UserTeam.team_id == team_id)
            .first()
        )

    def get_user_by_email(self, mail):
        return db.session.query(User).filter(User.email == mail).first()

    def get_user_by_document_edit_id(self, document_edit_id) -> int:
        document_edit = (
            Session.query(DocumentEdit)
            .filter(DocumentEdit.id == document_edit_id)
            .filter(DocumentEdit.active == True)
            .first()
        )
        if document_edit is None:
            raise NotFound("Document Edit not found")
        return int(document_edit.user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def create_user(self, username, email, hashed_password):
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def check_user_document_accessible(self, user_id, document_id):
        return (
            db.session.query(
                Document,
                Project.schema_id,
                DocumentRecommendation.id.label("document_recommendation_id"),
            )
            .select_from(UserTeam)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Project.team_id == Team.id)
            .join(Document, Document.project_id == Project.id)
            .outerjoin(
                DocumentRecommendation,
                and_(
                    Document.id == DocumentRecommendation.document_id,
                    DocumentRecommendation.document_edit_id is None,
                ),
            )
            .filter((Document.id == document_id) & (UserTeam.user_id == user_id))
            .first()
        )

    def check_user_schema_accessible(self, user_id, schema_id):
        return (
            Session.query(UserTeam)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Schema, Schema.team_id == Team.id)
            .filter((Schema.id == schema_id) & (UserTeam.user_id == user_id))
            .first()
        )

    def check_user_project_accessible(self, user_id, project_id):
        return (
            Session.query(UserTeam)
            .join(Project, Project.team_id == UserTeam.team_id)
            .filter((Project.id == project_id) & (UserTeam.user_id == user_id))
            .first()
        )
