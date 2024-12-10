from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from flask import request
from app.services.project_service import project_service
from app.dtos import create_project_input_model, create_project_output_model

ns = Namespace("projects", description="Project related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class ProjectRoutes(Resource):
    service = project_service

    @ns.expect(create_project_input_model, validate=True)
    @ns.marshal_with(create_project_output_model)
    def post(self):
        try:
            request_data = request.get_json()

            response = self.service.create_project(
                request_data["user_id"],
                request_data["team_id"],
                request_data["schema_id"],
                request_data["name"],
            )

            return response

        except exc.IntegrityError:
            raise BadRequest("Projectname already exists")
