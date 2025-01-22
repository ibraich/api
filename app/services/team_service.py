from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from app.repositories.team_repository import TeamRepository
from app.services.user_service import UserService, user_service


class TeamService:
    __team_repository: TeamRepository
    user_service: UserService

    def __init__(self, team_repository: TeamRepository, user_service):
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
                    "creator": self.user_service.get_user_by_id(team.creator_id),
                    "members": self.__get_team_members_by_team_id(team.id),
                }
                for team in teams
            ]
        }

    def get_team_by_id(self, team_id):
        teams = self.get_teams_by_user()
        for team in teams["teams"]:
            if team["id"] == team_id:
                return team
        raise BadRequest("Team not found or no access to this team")

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
            self.__add_user(team_id, new_member.id)
            return self.get_team_by_id(team_id)

    def __add_user(self, team_id, user_id):
        return self.__team_repository.add_user(team_id, user_id)

    def create_team(self, team_name):
        user_id = self.user_service.get_logged_in_user_id()

        team = self.__team_repository.create_team(team_name, user_id)
        self.__add_user(team.id, user_id)
        return self.get_team_by_id(team.id)

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
        return self.get_team_by_id(team_id)

    def get_team_by_project_id(self, project_id):
        if not isinstance(project_id, int) or project_id <= 0:
            raise BadRequest("Invalid project ID. Must be a positive integer.")

        team_id = self.__team_repository.get_team_by_project_id(project_id)
        if not team_id:
            raise NotFound("No team found for this project or project doesn't exist.")
        return team_id

    def update_team_name(self, team_id: int, new_name: str):
        """Update the name of a team."""
        if not new_name or not new_name.strip():
            raise BadRequest("Team name cannot be empty.")

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user_id, team_id)

        updated = self.__team_repository.update_team_name(team_id, new_name)
        if not updated:
            raise NotFound(f"Team with ID {team_id} not found.")
        return self.get_team_by_id(team_id)


team_service = TeamService(TeamRepository(), user_service)
