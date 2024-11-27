from app.services.schema_service import SchemaService, schema_service
from app.services.user_requests_service import (
    UserRequestsService,
    user_requests_service,
)
from app.repositories.project_repository import ProjectRepository, project_repository


class ProjectService:
    user_requests_service: UserRequestsService
    schema_service: SchemaService
    project_repository: ProjectRepository

    def __init__(self, project_repository, user_requests_service, schema_service):
        self.project_repository = project_repository
        self.user_requests_service = user_requests_service
        self.schema_service = schema_service

    def create_project(self, request_data):
        if (
            "user_id" not in request_data
            or "team_id" not in request_data
            or "name" not in request_data
            or "schema_id" not in request_data
        ):
            response = {"message": "Parameters missing"}
            return response, 400
        check_auth = self.user_requests_service.check_authentication(
            request_data["user_id"]
        )
        if check_auth[1] == 403:
            return check_auth
        check_team = self.user_requests_service.check_user_in_team(
            request_data["user_id"], request_data["team_id"]
        )
        if check_team[1] == 400:
            return check_team
        check_schema = self.schema_service.check_schema_exists(
            request_data["schema_id"]
        )
        if check_schema[1] == 400:
            return check_schema
        return project_repository.create_project(
            request_data["name"],
            request_data["user_id"],
            request_data["team_id"],
            request_data["schema_id"],
        )


project_service = ProjectService(
    project_repository, user_requests_service, schema_service
)
