from werkzeug.exceptions import BadRequest, Conflict, NotFound, Forbidden

from app.repositories.team_repository import TeamRepository
from app.services.user_service import UserService, user_service
from app.services.project_service import project_service, ProjectService


class TeamService:
    __team_repository: TeamRepository
    user_service: UserService
    project_service: ProjectService

    def __init__(self, team_repository, user_service, project_service):
        self.__team_repository = team_repository
        self.user_service = user_service
        self.project_service = project_service

    def get_teams_by_user(self, user_id):
        """
        Fetches all teams a user has access to

        :param user_id: User ID to query.
        :return: team_user_output_list_dto
        """
        teams = self.__team_repository.get_teams_by_user(user_id)
        if teams is None:
            return {"teams": []}
        return {"teams": [self.map_to_team_output_dto(team) for team in teams]}

    def __get_team_by_id(self, team_id):
        """
        Fetch team by team ID

        :param team_id: Team ID to query.
        :return: team_user_output_dto
        """
        team = self.__team_repository.get_team_by_id(team_id)
        if team is None:
            raise BadRequest("Team not found")
        return self.map_to_team_output_dto(team)

    def map_to_team_output_dto(self, team):
        """
        Maps team database object to output dto

        :param team: Team database object
        :return: team_user_output_dto
        """
        return {
            "id": team.id,
            "name": team.name,
            "creator": self.user_service.get_user_by_id(team.creator_id),
            "members": self.__get_team_members_by_team_id(team.id),
        }

    def __get_team_members_by_team_id(self, team_id):
        """
        Fetches all members of a team by team ID

        :param team_id: Team ID to query.
        :return: user_output_dto
        """
        members = self.__team_repository.get_members_of_team(team_id)
        return [
            {"id": member.id, "username": member.username, "email": member.email}
            for member in members
        ]

    def add_user_to_team(self, user_mail, team_id):
        """
        Adds user to a team
        :param user_mail: Email of user to add
        :param team_id: Team ID
        :return: team_user_output_dto
        :raises NotFound: If user does not exist
        :raises Conflict: If user already member of the team
        """
        new_member = self.user_service.get_user_by_email(user_mail)

        # If user does not exist, raise exception
        if new_member is None:
            raise NotFound("User not found")

        # Check that new member is not already part of the team
        try:
            self.user_service.check_user_in_team(new_member.id, team_id)
            raise Conflict("User is already part of the team")
        except Forbidden:
            self.__add_user(team_id, new_member.id)
            return self.__get_team_by_id(team_id)

    def __add_user(self, team_id, user_id):
        """
        Adds user to team, without validating inputs.

        :param team_id: Team ID to add user to
        :param user_id: user ID to add
        :return: Userteam database object
        """
        return self.__team_repository.add_user(team_id, user_id)

    def create_team(self, creator_id, team_name):
        """
        Creates a new team and sets creator as member.

        :param creator_id: Creator ID of the team
        :param team_name: Name of the new team
        :return: team_user_output_dto
        :raises BadRequest: If team name already exists
        """
        duplicate_team = self.__team_repository.get_team_by_name(team_name)
        if duplicate_team:
            raise BadRequest("Team with name " + team_name + " already exists")

        team = self.__team_repository.create_team(team_name, creator_id)
        self.__add_user(team.id, creator_id)
        return self.__get_team_by_id(team.id)

    def remove_user_from_team(self, user_mail, team_id):
        """
        Remove user from a team.

        :param user_mail: Email of user to delete
        :param team_id: Team ID to remove user from
        :return: team_user_output_dto
        :raises NotFound: If user does not exist
        :raises BadRequest: If user is not part of the team
        """
        member = self.user_service.get_user_by_email(user_mail)

        # If user does not exist, raise exception
        if member is None:
            raise NotFound("User not found")

        # Check that member is currently part of the team
        try:
            self.user_service.check_user_in_team(member.id, team_id)
        except Forbidden:
            raise BadRequest("User is not part of the team")

        self.__team_repository.remove_user(team_id, member.id)
        return self.__get_team_by_id(team_id)

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

        updated = self.__team_repository.update_team_name(team_id, new_name)
        if not updated:
            raise NotFound(f"Team with ID {team_id} not found.")
        return self.__get_team_by_id(team_id)

    def delete_team(self, team_id):
        success = self.__team_repository.delete_team(team_id)
        if not success:
            raise NotFound(f"Team with ID {team_id} not found.")
        projects = self.project_service.get_projects_by_team(team_id)
        for project in projects:
            self.project_service.soft_delete_project(project.id)
        return {"message": "Team set to inactive successfully."}


team_service = TeamService(TeamRepository(), user_service, project_service)
