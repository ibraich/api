from flask import session
from app.repositories.user_repository import UserRepository


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository):
        self.__user_repository = user_repository

    @staticmethod
    def check_authentication(user_id):
        if "user_id" not in session or user_id != session["user_id"]:
            response = {"message": "Unauthorized"}
            return response, 403
        return "", 200

    def check_user_in_team(self, user_id, team_id):
        return self.__user_repository.check_user_in_team(user_id, team_id)


user_service = UserService(UserRepository())
