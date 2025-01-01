from app.models import UserTeam, DocumentEdit, User
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
        return (
            db.session.query(User.id, User.username, User.email)
            .filter(User.email == mail)
            .first()
        )

    def get_user_by_document_edit_id(self, document_edit_id):
        document_edit = db.session.query(DocumentEdit).get(document_edit_id)
        return document_edit.user_id

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def create_user(self, username, email, hashed_password):
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
