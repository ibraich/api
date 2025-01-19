from werkzeug.exceptions import BadRequest, NotFound

from app.services.schema_service import SchemaService, schema_service
from app.services.user_service import (
    UserService,
    user_service,
)
from app.repositories.project_repository import ProjectRepository
from app.services.team_service import TeamService, team_service
from app.services.document_service import DocumentService, document_service


class ProjectService:
    user_service: UserService
    schema_service: SchemaService
    __project_repository: ProjectRepository
    team_service: TeamService
    document_service: DocumentService

    def __init__(
        self,
        project_repository,
        user_service,
        schema_service,
        team_service,
        document_service,
    ):
        self.__project_repository = project_repository
        self.user_service = user_service
        self.schema_service = schema_service
        self.team_service = team_service
        self.document_service = document_service

    def create_project(self, team_id, schema_id, projectname):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user_id, team_id)
        self.user_service.check_user_schema_accessible(user_id, schema_id)
        self.schema_service.fix_schema(schema_id)
        project = self.__project_repository.create_project(
            projectname,
            user_id,
            team_id,
            schema_id,
        )
        return {
            "id": project.id,
            "name": project.name,
            "team_id": project.team_id,
            "schema_id": project.schema_id,
            "creator_id": project.creator_id,
        }

    def team_is_in_project(self, team_id, document_edit_id):
        return team_id == self.__project_repository.get_team_id_by_document_edit_id(
            document_edit_id
        )

    def get_project_by_id(self, project_id):
        project = self.__project_repository.get_project_by_id(project_id)
        if project is None:
            raise BadRequest("Project not found")
        return project

    def get_projects_by_user(self):
        user_id = self.user_service.get_logged_in_user_id()
        projects = self.__project_repository.get_projects_by_user(user_id)
        if projects is None:
            return {"projects": []}
        return {
            "projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "creator_id": project.creator_id,
                    "team": {
                        "team_id": project.team_id,
                        "team_name": project.team_name,
                    },
                    "schema": {
                        "schema_id": project.schema_id,
                        "schema_name": project.schema_name,
                    },
                }
                for project in projects
            ]
        }

    def soft_delete_project(self, project_id):
        user_id = self.user_service.get_logged_in_user_id()
        team_id = self.team_service.get_team_by_project_id(project_id)
        self.user_service.check_user_in_team(user_id, team_id)
        if not isinstance(project_id, int) or project_id <= 0:
            raise BadRequest("Invalid project ID. Must be a positive integer.")

        success = self.__project_repository.soft_delete_project(project_id)
        if not success:
            raise NotFound("Project not found or already inactive.")

        self.document_service.bulk_soft_delete_documents_by_project_id(project_id)

        return {"message": "Project set to inactive successfully."}


project_service = ProjectService(
    ProjectRepository(), user_service, schema_service, team_service, document_service
)
