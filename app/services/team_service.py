from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from app.repositories.team_repository import TeamRepository
from app.services.user_service import UserService, user_service


class TeamService:
    __team_repository: TeamRepository
    user_service: UserService

    def __init__(self, team_repository, user_service):
        self.__team_repository = team_repository
        self.user_service = user_service

    def get_teams_by_user(self):
        current_user_id = self.user_service.get_logged_in_user_id()
        teams = self.__team_repository.get_teams_by_user(current_user_id)
        if teams is None:
            return {"teams": []}
        return {
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                    "creator_id": team.creator_id,
                    "members": self.__get_team_members_by_team_id(team.id),
                }
                for team in teams
            ]
        }

    def __get_team_members_by_team_id(self, team_id):
        members = self.__team_repository.get_members_of_team(team_id)
        return [
            {"id": member.id, "username": member.username, "email": member.email}
            for member in members
        ]

    def add_user_to_team(self, user_mail, team_id):
        new_member = self.user_service.get_user_by_email(user_mail)

        # If user does not exist, raise exception
        if new_member is None:
            raise BadRequest("User not found")

        # Check if logged-in user is part of the team
        user = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user, team_id)

        # Check that new member is not already part of the team
        try:
            self.user_service.check_user_in_team(new_member.id, team_id)
            raise Conflict("User is already part of the team")
        except BadRequest:
            self.add_user(team_id, new_member.id)
            return {
                "id": new_member.id,
                "username": new_member.username,
                "email": new_member.email,
            }

    def add_user(self, team_id, user_id):
        return self.__team_repository.add_user(team_id, user_id)

    def create_team(self, team_name):
        user_id = self.user_service.get_logged_in_user_id()

        team = self.__team_repository.create_team(team_name, user_id)
        self.add_user(team.id, user_id)
        return {
            "id": team.id,
            "name": team.name,
            "creator_id": team.creator_id,
        }

    def remove_user_from_team(self, user_mail, team_id):
        member = self.user_service.get_user_by_email(user_mail)

        # If user does not exist, raise exception
        if member is None:
            raise BadRequest("User not found")

        # Check if logged-in user is part of the team
        user = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user, team_id)

        # Check that member is currently part of the team
        try:
            self.user_service.check_user_in_team(member.id, team_id)
        except:
            raise BadRequest("User is not part of the team")

        self.__team_repository.remove_user(team_id, member.id)
        return {
            "id": member.id,
            "username": member.username,
            "email": member.email,
        }

    def get_team_by_project_id(self, project_id):
        if not isinstance(project_id, int) or project_id <= 0:
            raise BadRequest("Invalid project ID. Must be a positive integer.")

        team_id = self.__team_repository.get_team_by_project_id(project_id)
        if not team_id:
            raise NotFound("No team found for this project or project doesn't exist.")
        return team_id


team_service = TeamService(TeamRepository(), user_service)
