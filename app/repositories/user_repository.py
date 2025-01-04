from werkzeug.exceptions import NotFound

from app.models import UserTeam, DocumentEdit, User, Team, Project, Document
from app.repositories.base_repository import BaseRepository
from app.db import db


class UserRepository(BaseRepository):
    def check_user_in_team(self, user_id, team_id):
        return (
            db.session.query(UserTeam)
            .filter(UserTeam.user_id == user_id, UserTeam.team_id == team_id)
            .first()
        )

    def get_user_by_email(self, mail):
        return db.session.query(User).filter(User.email == mail).first()

    def get_user_by_document_edit_id(self, document_edit_id):
        document_edit = db.session.query(DocumentEdit).get(document_edit_id)
        if document_edit is None:
            raise NotFound("Document Edit not found")
        return document_edit.user_id

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def create_user(self, username, email, hashed_password):
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def check_user_document_accessible(self, user_id, document_id):
        return (
            db.session.query(UserTeam)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Project.team_id == Team.id)
            .join(Document, Document.project_id == Project.id)
            .filter((Document.id == document_id) & (UserTeam.user_id == user_id))
            .first()
        )
