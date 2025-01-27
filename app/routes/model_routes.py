from flask_restx import Namespace
import requests
from werkzeug.exceptions import BadRequest
from app.routes.base_routes import AuthorizedBaseRoute
from flask import request, current_app
from app.dtos import get_recommendation_models_output_dto

ns = Namespace("models", description="Document-Annotation related operations")


class ModelBaseRoute(AuthorizedBaseRoute):
    pass


@ns.route("/recommendation")
class ModelRoutes(ModelBaseRoute):

    @ns.doc(
        description="Fetch possible model types for recommendation generation from pipeline microservice"
    )
    @ns.marshal_with(get_recommendation_models_output_dto)
    def get(self):

        steps = ["mention", "entity", "relation"]
        response = {}

        for step in steps:

            url = current_app.config.get("PIPELINE_URL") + "/steps/" + step
            headers = {"Content-Type": "application/json"}

            step_response = requests.get(url=url, headers=headers)
            if step_response.status_code != 200:
                raise BadRequest(step_response.text)

            response[step] = step_response.json()

        return response
