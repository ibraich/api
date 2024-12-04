from sqlalchemy import exc
from werkzeug.exceptions import BadRequest, HTTPException
from flask_restx import Resource, fields, Namespace
from flask import request, jsonify
from app.services.project_service import project_service

api = Namespace("projects", description="Project related operations")

create_project_model = api.model(
    "CreateProject",
    {
        "name": fields.String(required=True, example="example"),
        "user_id": fields.Integer(required=True),
        "team_id": fields.Integer(required=True),
        "schema_id": fields.Integer(required=True),
    },
)


@api.route("/")
class ProjectRoutes(Resource):
    service = project_service

    @api.expect(create_project_model, validate=True)
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

            response, status = self.service.create_project(
                user_id, team_id, schema_id, request_data["name"]
            )

            return jsonify(response), status

        except exc.IntegrityError as e:
            return {"message": "Projectname already exists"}, 400

        except HTTPException as e:
            return {"message": str(e)}, e.code

        except Exception as e:
            return (
                {"message": "An unexpected error occurred.", "details": str(e)},
                500,
            )
