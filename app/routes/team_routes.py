from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from flask import request
from app.dtos import team_input_dto, team_output_dto, team_member_input_dto, team_member_output_dto, team_user_output_list_dto
from app.services.team_service import team_service

ns = Namespace("teams", description="Team related operations")


@ns.route("/members")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamMemberRoutes(Resource):
    service = team_service

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

@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class TeamRoutes(Resource):
    service = team_service

    @ns.doc(description="Fetch all teams of current logged-in user")
    @ns.marshal_with(team_user_output_list_dto)
    def get(self):

        response = self.service.get_teams_by_user()
        return response
      
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
