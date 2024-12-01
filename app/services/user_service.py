from flask import session
from werkzeug.exceptions import BadRequest, Forbidden

from app.repositories.user_repository import UserRepository


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository):
        self.__user_repository = user_repository

    @staticmethod
    def check_authentication(user_id):
        if "user_id" not in session or user_id != session["user_id"]:
            raise Forbidden("You need to be logged in")

    def check_user_in_team(self, user_id, team_id):
        if self.__user_repository.check_user_in_team(user_id, team_id) is None:
            raise BadRequest("You have to be in a team")


user_service = UserService(UserRepository())
