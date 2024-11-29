from app.services.schema_service import SchemaService, schema_service
from app.services.user_service import (
    UserService,
    user_service,
)
from app.repositories.project_repository import ProjectRepository
from app.services.team_service import TeamService, team_service


class ProjectService:
    user_service: UserService
    schema_service: SchemaService
    team_service: TeamService

    __project_repository: ProjectRepository

    def __init__(self, project_repository, user_service, schema_service, team_service):
        self.__project_repository = project_repository
        self.user_service = user_service
        self.schema_service = schema_service
        self.team_service = team_service

    def create_project(self, request_data):
        if (
            "user_id" not in request_data
            or "team_id" not in request_data
            or "name" not in request_data
            or "schema_id" not in request_data
        ):
            response = {"message": "Parameters missing"}
            return response, 400
        check_auth = self.user_service.check_authentication(request_data["user_id"])
        if check_auth[1] == 403:
            return check_auth
        check_team = self.user_service.check_user_in_team(
            request_data["user_id"], request_data["team_id"]
        )
        if check_team[1] == 400:
            return check_team
        check_schema = self.schema_service.check_schema_exists(
            request_data["schema_id"]
        )
        if check_schema[1] == 400:
            return check_schema
        return self.__project_repository.create_project(
            request_data["name"],
            request_data["user_id"],
            request_data["team_id"],
            request_data["schema_id"],
        )

    def get_projects_by_team(self, team_id):
        return self.__project_repository.get_projects_by_team(team_id)

    def get_projects_by_user(self, user_id):
        teams = self.team_service.get_teams_by_user(user_id)
        projects_of_user = []
        if teams is None:
            return []
        for team in teams:
            projects = self.get_projects_by_team(team.id)
            if projects is None:
                continue
            for project in projects:
                projects_of_user.append(project)
        return projects_of_user


project_service = ProjectService(
    ProjectRepository(), user_service, schema_service, team_service
)
