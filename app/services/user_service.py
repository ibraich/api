from datetime import timedelta
from app.config import Config
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository
from flask_jwt_extended import create_access_token, get_jwt_identity


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository):
        self.__user_repository = user_repository

    def check_user_in_team(self, user_id, team_id):
        """
        Checks if user is part of the team

        :param user_id: User ID
        :param team_id: Team ID
        :raises Forbidden: If user does not belong to team
        """
        if self.__user_repository.check_user_in_team(user_id, team_id) is None:
            raise Forbidden("You are not part of this team")

    def get_logged_in_user_id(self):
        """
        Get currently logged-in user

        :return: User ID
        :raises Unauthorized: If no user is not logged in
        """
        try:
            user_id = int(get_jwt_identity())
            return user_id
        except Exception as e:
            raise Unauthorized(str(e))

    def get_user_by_email(self, mail):
        return self.__user_repository.get_user_by_email(mail)

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
        """
        Checks if user has access to document

        :param user_id: User ID
        :param document_id: Document ID
        :raises Forbidden: If user has no access to document
        """
        document = self.__user_repository.check_user_document_accessible(
            user_id, document_id
        )
        if document is None:
            raise Forbidden("You cannot access this document")

    def check_user_document_edit_accessible(self, user_id, document_edit_id):
        """
        Checks if user has access to document edit

        :param user_id: User ID
        :param document_edit_id: DocumentEdit ID
        :raises Forbidden: If user has no access to document edit
        """
        document_edit_user_id = self.__user_repository.get_user_by_document_edit_id(
            document_edit_id
        )

        if int(user_id) != int(document_edit_user_id):
            raise Forbidden("You cannot access this document edit")

    def check_user_schema_accessible(self, user_id, schema_id):
        """
        Checks if user has access to schema

        :param user_id: User ID
        :param schema_id: Schema ID
        :raises Forbidden: If user has no access to schema
        """
        if (
            self.__user_repository.check_user_schema_accessible(user_id, schema_id)
            is None
        ):
            raise Forbidden("You cannot access this schema")

    def check_user_project_accessible(self, user_id, project_id):
        """
        Checks if user has access to project

        :param user_id: User ID
        :param project_id: Project ID
        :raises Forbidden: If user has no access to project
        """
        if (
            self.__user_repository.check_user_project_accessible(user_id, project_id)
            is None
        ):
            raise Forbidden("You cannot access this project")

    def check_user_entity_accessible(self, user_id, entity_id):
        """
        Checks if user has access to entity

        :param user_id: User ID
        :param entity_id: Entity ID
        :raises Forbidden: If user has no access to entity
        """
        if (
            self.__user_repository.check_user_entity_accessible(user_id, entity_id)
            is None
        ):
            raise Forbidden("You cannot access this entity")

    def check_user_relation_accessible(self, user_id, relation_id):
        """
        Checks if user has access to relation

        :param user_id: User ID
        :param relation_id: Relation ID
        :raises Forbidden: If user has no access to relation
        """
        if (
            self.__user_repository.check_user_relation_accessible(user_id, relation_id)
            is None
        ):
            raise Forbidden("You cannot access this relation")

    def check_user_mention_accessible(self, user_id, mention_id):
        """
        Checks if user has access to mention

        :param user_id: User ID
        :param mention_id: Mention ID
        :raises Forbidden: If user has no access to mention
        """
        if (
            self.__user_repository.check_user_mention_accessible(user_id, mention_id)
            is None
        ):
            raise Forbidden("You cannot access this mention")

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

    def update_user_data(self, user_id, username=None, email=None, password=None):
        """
        Update user information by calling the repository.

        :param user_id: ID of the user
        :param username: New username (optional).
        :param email: New email (optional).
        :param password: New password (optional).
        :raises BadRequest: If no fields to update are provided.
        :raises NotFound: If the user is not found.
        :return: Updated user data.
        """
        if not any([username, email, password]):
            raise BadRequest("No fields to update provided.")

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
        """
        Fetch user by its ID

        :param user_id: User ID
        :return: user_output_dto
        :raises NotFound: If the user does not exist
        """
        user = self.__user_repository.get_user_by_id(user_id)
        if user is None:
            return NotFound("User not found")
        return {"id": user.id, "username": user.username, "email": user.email}


user_service = UserService(UserRepository())
