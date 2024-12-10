from sqlalchemy import exc
from werkzeug.exceptions import BadRequest, HTTPException, InternalServerError
from flask_restx import Resource, fields, Namespace
from flask import request, jsonify
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

            if (
                "user_id" not in request_data
                or "team_id" not in request_data
                or "name" not in request_data
                or "schema_id" not in request_data
            ):
                raise BadRequest(
                    "User ID, Team Id, Projectname, Schema ID are required."
                )

            user_id = request_data["user_id"]
            team_id = request_data["team_id"]
            schema_id = request_data["schema_id"]
            try:
                user_id = int(user_id)
                team_id = int(team_id)
                schema_id = int(schema_id)
            except:
                raise BadRequest("User ID, Team ID, Schema ID must be a valid integer.")

            response = self.service.create_project(
                user_id, team_id, schema_id, request_data["name"]
            )

            return response

        except exc.IntegrityError as e:
            raise BadRequest("Projectname already exists")
