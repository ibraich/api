from datetime import timedelta
from app.config import Config
from flask import session
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository
from flask_jwt_extended import create_access_token, get_jwt_identity


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository):
        self.__user_repository = user_repository

    def check_user_in_team(self, user_id, team_id):
        if self.__user_repository.check_user_in_team(user_id, team_id) is None:
            raise BadRequest("You are not part of this team")

    def get_logged_in_user_id(self):
        try:
            user_id = int(get_jwt_identity())
            return user_id
        except Exception as e:
            raise Unauthorized(str(e))

    def get_user_by_email(self, mail):
        return self.__user_repository.get_user_by_email(mail)

    def get_user_by_document_edit_id(self, document_edit_id):
        return self.__user_repository.get_user_by_document_edit_id(document_edit_id)

    def get_user_by_username(self, username):
        return self.__user_repository.get_user_by_username(username)

    def create_user(self, username, email, hashed_password):
        return self.__user_repository.create_user(username, email, hashed_password)

    def signup(self, username, email, password):
        if self.get_user_by_username(username):
            raise BadRequest("Username already exists")
        if self.get_user_by_email(email):
            raise BadRequest("Email already exists")

        if not password or len(password) < 6:  # Example validation
            raise BadRequest("Password must be at least 6 characters long")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        self.create_user(username, email, hashed_password)

    def check_user_document_accessible(self, user_id, document_id):
        document = self.__user_repository.check_user_document_accessible(
            user_id, document_id
        )
        if document is None:
            raise Forbidden("You cannot access this document")
        return document

    def check_user_document_edit_accessible(self, user_id, document_edit_id):
        document_edit_user_id = self.get_user_by_document_edit_id(document_edit_id)

        if int(user_id) != int(document_edit_user_id):
            raise NotFound("The logged in user does not belong to this document.")

    def check_user_schema_accessible(self, user_id, schema_id):
        if (
            self.__user_repository.check_user_schema_accessible(user_id, schema_id)
            is None
        ):
            raise Forbidden("You cannot access this schema")

    def check_user_project_accessible(self, user_id, project_id):
        if (
            self.__user_repository.check_user_project_accessible(user_id, project_id)
            is None
        ):
            raise Forbidden("You cannot access this project")

    def login(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            raise Unauthorized("Invalid email or password")

        if not check_password_hash(user.password, password):
            raise Unauthorized("Invalid email or password")
        user_id_str = str(user.id)
        expires_delta = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
        token = create_access_token(identity=user_id_str, expires_delta=expires_delta)
        return {"token": token}

    def update_user_data(self, username=None, email=None, password=None):
        """
        Update user information by calling the repository.

        :param username: New username (optional).
        :param email: New email (optional).
        :param password: New password (optional).
        :raises BadRequest: If no fields to update are provided.
        :raises NotFound: If the user is not found.
        :return: Updated user data.
        """
        if not any([username, email, password]):
            raise BadRequest("No fields to update provided.")

        user_id = self.get_logged_in_user_id()

        if username and self.get_user_by_username(username):
            raise BadRequest("Username already exists")
        if email and self.get_user_by_email(email):
            raise BadRequest("Email already exists")

        updated_user = self.__user_repository.update_user_data(
            user_id=user_id,
            username=username,
            email=email,
            password=password,
        )
        return {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
        }

    def get_user_by_id(self, user_id):
        user = self.__user_repository.get_user_by_id(user_id)
        if user is None:
            return BadRequest("User not found")
        return {"id": user.id, "username": user.username, "email": user.email}


user_service = UserService(UserRepository())
