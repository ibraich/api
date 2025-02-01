from werkzeug.exceptions import BadRequest, Conflict, NotFound

from app.repositories import document_repository, project_repository
from app.repositories.team_repository import TeamRepository
from app.services import document_service, project_service
from app.services.user_service import UserService, user_service
from app.services import document_service

class TeamService:
    __team_repository: TeamRepository
    user_service: UserService

    def __init__(self, team_repository, user_service):
        self.__team_repository = team_repository
        self.user_service = user_service
        self.project_service = project_service
        self.document_service = document_service
        document_service = document_service.DocumentService(document_repository)
        project_service = project_service.ProjectService(project_repository)
        team_service = TeamService(team_repository, project_service, document_service)

    def get_teams_by_user(self, user_id):
        teams = self.__team_repository.get_teams_by_user(user_id)
        if teams is None:
            return {"teams": []}
        return {"teams": [self.map_to_team_output_dto(team) for team in teams]}

    def get_team_by_id(self, team_id):
        team = self.__team_repository.get_team_by_id(team_id)
        if team is None:
            raise BadRequest("Team not found")
        return self.map_to_team_output_dto(team)

    def map_to_team_output_dto(self, team):
        return {
            "id": team.id,
            "name": team.name,
            "creator": self.user_service.get_user_by_id(team.creator_id),
            "members": self.__get_team_members_by_team_id(team.id),
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

        # Check that new member is not already part of the team
        try:
            self.user_service.check_user_in_team(new_member.id, team_id)
            raise Conflict("User is already part of the team")
        except BadRequest:
            self.__add_user(team_id, new_member.id)
            return self.get_team_by_id(team_id)

    def __add_user(self, team_id, user_id):
        return self.__team_repository.add_user(team_id, user_id)

    def create_team(self, creator_id, team_name):
        duplicate_team = self.__team_repository.get_team_by_name(team_name)
        if duplicate_team:
            raise BadRequest("Team with name " + team_name + " already exists")

        team = self.__team_repository.create_team(team_name, creator_id)
        self.__add_user(team.id, creator_id)
        return self.get_team_by_id(team.id)

    def remove_user_from_team(self, user_mail, team_id):
        member = self.user_service.get_user_by_email(user_mail)

        # If user does not exist, raise exception
        if member is None:
            raise BadRequest("User not found")

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

        updated = self.__team_repository.update_team_name(team_id, new_name)
        if not updated:
            raise NotFound(f"Team with ID {team_id} not found.")
        return self.get_team_by_id(team_id)

    def soft_delete_team(self, team_id):
        # Validate input
        if not isinstance(team_id, int) or team_id <= 0:
            raise BadRequest("Invalid team ID. Must be a positive integer.")

        # Mark the team as inactive
        success = self.team_repository.soft_delete_team(team_id)
        if not success:
            raise NotFound("Team not found or already inactive.")

        # Fetch all projects associated with the team
        project_ids = self.project_service.get_project_ids_by_team_id(team_id)
        if not project_ids:
            return {"message": "Team set to inactive successfully. No projects to deactivate."}

        # Mark all projects as inactive
        for project_id in project_ids:
            self.project_service.soft_delete_project(project_id)

        # Ensure all related documents and edits are marked inactive via document service
        for project_id in project_ids:
            self.document_service.bulk_soft_delete_documents_by_project_id(project_id)

        return {"message": "Team and all related records set to inactive successfully."}

team_service = TeamService(TeamRepository(), user_service)
