import requests
from flask import request, current_app
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest

from app.dtos import (
    schema_output_dto,
    schema_output_list_dto,
    model_train_input,
    model_train_output_list_dto,
    schema_input_dto,
    get_recommendation_models_output_dto,
)
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.schema_service import schema_service, SchemaService

ns = Namespace("schemas", description="Schema related operations")


class SchemaBaseRoute(AuthorizedBaseRoute):
    service: SchemaService = schema_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaResource(SchemaBaseRoute):

    @ns.marshal_with(schema_output_list_dto)
    def get(self):
        """
        Fetch all schemas the user has access to
        """
        user_id = self.user_service.get_logged_in_user_id()

        return self.service.get_schemas_by_user(user_id)

    @ns.doc(
        params={
            "team_id": {
                "type": "integer",
                "required": True,
                "description": "Target team of the schema.",
            }
        }
    )
    @ns.marshal_with(schema_output_dto)
    @ns.expect(schema_input_dto)
    def post(self):
        """
        Creates a schema for given team ID
        """
        import_schema = request.get_json()

        team_id = request.args.get("team_id")
        self.verify_positive_integer(team_id)

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_in_team(user_id, team_id)

        return self.service.create_extended_schema(import_schema, int(team_id))


@ns.route("/<int:schema_id>")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaQueryResource(SchemaBaseRoute):

    @ns.marshal_with(schema_output_dto)
    def get(self, schema_id):
        """
        Fetch schema by schema ID
        """
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_schema_accessible(user_id, schema_id)

        response = self.service.get_schema_by_id(schema_id)
        return response


@ns.route("/<int:schema_id>/recommendation")
class ModelRoutes(SchemaBaseRoute):

    @ns.marshal_with(get_recommendation_models_output_dto)
    def get(self, schema_id):
        """
        Fetch recommendation models  of schema with possible settings-
        """

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_schema_accessible(user_id, schema_id)

        models = schema_service.get_models_by_schema(schema_id)

        steps = ["mention", "entity", "relation"]
        response = {}

        for index, step in enumerate(steps):

            url = current_app.config.get("PIPELINE_URL") + "/steps/" + step
            headers = {"Content-Type": "application/json"}

            step_response = requests.get(url=url, headers=headers)
            if step_response.status_code != 200:
                raise BadRequest(step_response.text)

            step_models = []
            response_json = step_response.json()

            for pipeline_model in response_json:

                # Add model from pipeline only if it is a possible model for this schema
                existing_recommendation_model = next(
                    (
                        model
                        for model in models
                        if model["type"] == pipeline_model["model_type"]
                        and model["step"]["id"] == index + 1
                    ),
                    None,
                )
                if existing_recommendation_model is not None:
                    pipeline_model["name"] = existing_recommendation_model["name"]
                    pipeline_model["id"] = existing_recommendation_model["id"]
                    step_models.append(pipeline_model)

            response[step] = step_models

        return response


@ns.route("/<int:schema_id>/train")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaTrainResource(SchemaBaseRoute):

    @ns.expect(model_train_input)
    @ns.marshal_with(model_train_output_list_dto)
    def post(self, schema_id):
        """
        Train a recommendation model for a given schema ID
        """
        data = request.json

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_schema_accessible(user_id, schema_id)

        response = self.service.train_model_for_schema(
            schema_id, data["model_name"], data["model_type"], data["model_steps"]
        )
        return response
