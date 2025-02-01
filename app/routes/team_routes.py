from flask_restx import Namespace, Resource
from flask import request, jsonify
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from app.dtos import (
    team_input_dto,
    team_member_input_dto,
    team_user_output_list_dto,
    team_user_output_dto,
)
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.team_service import team_service, TeamService

ns = Namespace("teams", description="Team related operations")


class TeamBaseRoute(AuthorizedBaseRoute):
    service: TeamService = team_service


@ns.route("/<int:team_id>/members")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamMemberRoutes(TeamBaseRoute):

    @ns.doc(description="Add a user to a team")
    @ns.expect(team_member_input_dto)
    @ns.marshal_with(team_user_output_dto)
    def post(self, team_id):
        request_data = request.get_json()

        user = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user, team_id)

        response = self.service.add_user_to_team(
            request_data["user_mail"],
            team_id,
        )
        return response

    @ns.doc(description="Remove a user from a team")
    @ns.expect(team_member_input_dto)
    @ns.marshal_with(team_user_output_dto)
    def delete(self, team_id):
        request_data = request.get_json()

        user = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user, team_id)

        response = self.service.remove_user_from_team(
            request_data["user_mail"],
            team_id,
        )
        return response


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamRoutes(TeamBaseRoute):

    @ns.doc(description="Fetch all teams of current logged-in user")
    @ns.marshal_with(team_user_output_list_dto)
    def get(self):
        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.get_teams_by_user(user_id)
        return response

    @ns.doc(description="Create a new team")
    @ns.expect(team_input_dto)
    @ns.marshal_with(team_user_output_dto)
    def post(self):
        request_data = request.get_json()

        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.create_team(
            user_id,
            request_data["name"],
        )
        return response


@ns.route("/<int:team_id>")
class TeamUpdateResource(TeamBaseRoute):
    """API endpoint to update team properties."""

    @ns.expect(team_input_dto)
    @ns.marshal_with(team_user_output_dto)
    def put(self, team_id):
        """Update the name of a team."""
        data = request.json

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user_id, team_id)

        team = self.service.update_team_name(team_id, data["name"])
        return team


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamRoutes(Resource):

    @ns.doc(description="Fetch all teams of current logged-in user")
    @ns.marshal_with(team_user_output_list_dto)
    def get(self):
        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.get_teams_by_user(user_id)
        return response

    @ns.doc(description="Create a new team")
    @ns.expect(team_input_dto)
    @ns.marshal_with(team_user_output_dto)
    def post(self):
        request_data = request.get_json()

        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.create_team(
            user_id,
            request_data["name"],
        )
        return response

    @ns.doc(description="Delete a team by marking it as inactive")
    @ns.response(200, "Team deleted successfully")
    @ns.response(400, "Invalid team ID")
    def delete(self):
        team_id = request.args.get("team_id", type=int)

        if not team_id:
            raise BadRequest("Missing team_id parameter")

        try:
            result = self.service.soft_delete_team(team_id)
            return jsonify(result), 200
        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except NotFound as e:
            return jsonify({"error": str(e)}), 404