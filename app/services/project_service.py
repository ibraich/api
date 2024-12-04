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

    def create_project(self, user_id, team_id, schema_id, projectname):
        self.user_service.check_authentication(user_id)
        self.user_service.check_user_in_team(user_id, team_id)
        self.schema_service.check_schema_exists(schema_id)
        project = self.__project_repository.create_project(
            projectname,
            user_id,
            team_id,
            schema_id,
        )
        return (
            {
                "project_id": project.id,
                "project_name": project.name,
                "project_team_id": project.team_id,
                "project_schema_id": project.schema_id,
            },
            200,
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
