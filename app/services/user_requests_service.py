from flask import session
from app.db import db
from app.models import UserTeam


class UserRequestsService:

    @staticmethod
    def check_authentication(user_id):
        if "user_id" not in session or user_id != session["user_id"]:
            response = {"message": "Unauthorized"}
            return response, 403
        return "", 200

    @staticmethod
    def check_user_in_team(user_id, team_id):
        if (
            db.session.query(UserTeam)
            .filter(UserTeam.user_id == user_id, UserTeam.team_id == team_id)
            .first()
            is None
        ):
            response = {"message": "User not in team"}
            return response, 400
        return "", 200


user_requests_service = UserRequestsService()
