from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from flask_restx import Namespace

from app.dtos import (
    schema_output_dto,
    schema_output_list_dto,
    model_train_input,
    model_train_output_list_dto,
    schema_input_dto,
)
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.schema_service import schema_service, SchemaService

ns = Namespace("schemas", description="Schema related operations")


class SchemaBaseRoute(AuthorizedBaseRoute):
    service = schema_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaResource(SchemaBaseRoute):

    @ns.doc(description="Fetch all schemas of current logged-in user")
    @ns.marshal_with(schema_output_list_dto)
    def get(self):
        return self.service.get_schemas_by_user()

    @ns.doc(description="Create schema.")
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
        import_schema = request.get_json()

        team_id = request.args.get("team_id")
        self.verify_positive_integer(team_id)

        return self.service.create_extended_schema(import_schema, team_id)


@ns.route("/<int:schema_id>")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaQueryResource(SchemaBaseRoute):

    @ns.doc(description="Get schema by schema ID")
    @ns.marshal_with(schema_output_dto)
    def get(self, schema_id):
        if not schema_id:
            raise BadRequest("Schema ID is required.")

        response = self.service.get_schema_by_id(schema_id)
        return response


@ns.route("/<int:schema_id>/train")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaTrainResource(SchemaBaseRoute):

    @ns.doc(description="Train model for given schema ID")
    @ns.expect(model_train_input)
    @ns.marshal_with(model_train_output_list_dto)
    def post(self, schema_id):
        if not schema_id:
            raise BadRequest("Schema ID is required.")

        data = request.json

        response = self.service.train_model_for_schema(
            schema_id, data["model_name"], data["model_type"], data["model_steps"]
        )
        return response


@ns.route("/<int:schema_id>")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaUpdateResource(SchemaBaseRoute):

    @ns.doc(description="Update schema by schema ID")
    @ns.doc(
        params={
            "schema_id": {
                "type": "integer",
                "required": True,
                "description": "ID of the schema to be updated."
            },
        }
    )
    @ns.expect(schema_input_dto)
    def put(self, schema_id):
        """
        Update the schema by adding or removing mentions, relations, and constraints.
        """
        if not schema_id:
            raise BadRequest("Schema ID is required.")

        data = request.get_json()
        mentions = data.get("mentions", [])
        relations = data.get("relations", [])
        constraints = data.get("constraints", [])

        try:
            response = self.service.update_schema(schema_id, mentions, relations, constraints)
            return jsonify({"message": "Schema updated successfully.", "data": response}), 200
        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred."}), 500