from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Namespace
from flask import request

from app.routes.base_routes import AuthorizedBaseRoute
from app.services.project_service import project_service
from app.dtos import (
    project_input_dto,
    project_user_output_list_dto,
    project_delete_output_model,
    project_list_dto,
)

ns = Namespace("projects", description="Project related operations")


class ProjectBaseRoute(AuthorizedBaseRoute):
    service = project_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class ProjectRoutes(ProjectBaseRoute):

    @ns.doc(description="Create a new project")
    @ns.expect(project_input_dto)
    @ns.marshal_with(project_list_dto)
    def post(self):
        try:
            request_data = request.get_json()

            return self.service.create_project(
                request_data["team_id"],
                request_data["schema_id"],
                request_data["name"],
            )
        except exc.IntegrityError:
            raise BadRequest("Projectname already exists")

    @ns.doc(description="Fetch all projects of current logged-in user")
    @ns.marshal_with(project_user_output_list_dto)
    def get(self):

        response = self.service.get_projects_by_user()
        return response


@ns.route("/<int:project_id>")
@ns.doc(params={"project_id": "Project ID to soft-delete"})
@ns.response(404, "Project not found")
class ProjectDeletionResource(ProjectBaseRoute):

    @ns.marshal_with(
        project_delete_output_model, description="Project set to inactive successfully"
    )
    @ns.doc(description="Soft-delete a Project by setting 'active' to False")
    def delete(self, project_id):
        response = self.service.soft_delete_project(project_id)
        return response
