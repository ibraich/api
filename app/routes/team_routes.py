from sqlalchemy import exc
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from flask import request
from app.dtos import team_user_output_list_dto
from app.services.team_service import team_service

ns = Namespace("teams", description="Team related operations")


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
