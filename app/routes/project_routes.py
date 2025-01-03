from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from flask import request
from app.services.project_service import project_service
from app.dtos import project_input_dto, project_output_dto, project_user_output_list_dto
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
