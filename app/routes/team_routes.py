from sqlalchemy import exc
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
from flask_restx import Resource, Namespace
from flask import request
from app.dtos import (
    team_input_dto,
    team_output_dto,
    team_member_input_dto,
    team_member_output_dto,
    team_user_output_list_dto,
)
from app.services.team_service import team_service

ns = Namespace("teams", description="Team related operations")


@ns.route("/members")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamMemberRoutes(Resource):
    service = team_service

    @jwt_required()
    @ns.doc(description="Add a user to a team")
    @ns.expect(team_member_input_dto, validate=True)
    @ns.marshal_with(team_member_output_dto)
    def post(self):
        request_data = request.get_json()

        response = self.service.add_user_to_team(
            request_data["user_mail"],
            request_data["team_id"],
        )

        return response

    @jwt_required()
    @ns.doc(description="Remove a user from a team")
    @ns.expect(team_member_input_dto, validate=True)
    @ns.marshal_with(team_member_output_dto)
    def delete(self):
        request_data = request.get_json()

        response = self.service.remove_user_from_team(
            request_data["user_mail"],
            request_data["team_id"],
        )

        return response


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamRoutes(Resource):
    service = team_service

    @jwt_required()
    @ns.doc(description="Fetch all teams of current logged-in user")
    @ns.marshal_with(team_user_output_list_dto)
    def get(self):
        response = self.service.get_teams_by_user()
        return response

    @jwt_required()
    @ns.doc(description="Create a new team")
    @ns.expect(team_input_dto, validate=True)
    @ns.marshal_with(team_output_dto)
    def post(self):
        try:
            request_data = request.get_json()

            response = self.service.create_team(
                request_data["name"],
            )

            return response

        except exc.IntegrityError:
            raise BadRequest("Teamname already exists")

@ns.route("/<int:team_id>")
class TeamUpdateResource(Resource):
    """API endpoint to update team properties."""

    @ns.expect(team_input_dto, validate=True)
    @jwt_required()
    def put(self, team_id):
        """Update the name of a team."""
        try:
            data = request.json
            team_service.update_team_name(team_id, data["name"])
            return {"message": "Team updated successfully."}, 200
        except BadRequest as e:
            return {"error": str(e)}, 400
        except NotFound as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": "An unexpected error occurred."}, 500