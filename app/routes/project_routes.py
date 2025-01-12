from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from flask import request
from app.services.project_service import project_service
from app.dtos import project_input_dto, project_output_dto, project_user_output_list_dto, project_delete_input_model, \
    project_delete_output_model
from flask_jwt_extended import jwt_required

ns = Namespace("projects", description="Project related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class ProjectRoutes(Resource):
    service = project_service

    @jwt_required()
    @ns.doc(description="Create a new project")
    @ns.expect(project_input_dto, validate=True)
    @ns.marshal_with(project_output_dto)
    def post(self):
        try:
            request_data = request.get_json()

            response = self.service.create_project(
                request_data["team_id"],
                request_data["schema_id"],
                request_data["name"],
            )

            return response

        except exc.IntegrityError:
            raise BadRequest("Projectname already exists")

    @jwt_required()
    @ns.doc(description="Fetch all projects of current logged-in user")
    @ns.marshal_with(project_user_output_list_dto)
    def get(self):

        response = self.service.get_projects_by_user()
        return response

    @ns.route("/<int:project_id>")
    @ns.doc(params={"project_id": "Project ID to soft-delete"})
    @ns.response(400, "Invalid input")
    @ns.response(404, "Project not found")
    @ns.response(200, "Project set to inactive successfully")
    class ProjectDeletionResource(Resource):
        service = project_service

        @jwt_required()
        @ns.marshal_with(project_delete_output_model)
        @ns.doc(description="Soft-delete a Project by setting 'active' to False")
        def delete(self, project_id):
            response = self.service.soft_delete_project(project_id)
            return response
