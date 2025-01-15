from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from app.dtos import schema_output_dto, schema_output_list_dto
from app.services.schema_service import schema_service
from flask_jwt_extended import jwt_required
from flask import Flask, request, jsonify

ns = Namespace("schemas", description="Schema related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaResource(Resource):
    service = schema_service

    @jwt_required()
    @ns.doc(description="Fetch all schemas of current logged-in user")
    @ns.marshal_with(schema_output_list_dto)
    def get(self):
        return self.service.get_schemas_by_user()


@ns.route("/<int:schema_id>")
@ns.doc(params={"schema_id": "A Schema ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaQueryResource(Resource):
    service = schema_service

    @jwt_required()
    @ns.doc(description="Get schema by schema ID")
    @ns.marshal_with(schema_output_dto)
    def get(self, schema_id):
        if not schema_id:
            raise BadRequest("Schema ID is required.")

        response = self.service.get_schema_by_id(schema_id)
        return response

@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class SchemaResource(Resource):
    service = schema_service

    @jwt_required()
    @ns.doc(description="Create a new schema")
    def post(self):
        """
        Create a new schema.
        """
        user_id = self.service.user_service.get_logged_in_user_id()
        data = request.json

        # Validate input data
        required_fields = ["team_id", "name", "modelling_language_id", "mentions", "relations", "constraints"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        schema_id = self.service.create_schema(
            team_id=data["team_id"],
            user_id=user_id,
            name=data["name"],
            modelling_language_id=data["modelling_language_id"],
            mentions=data["mentions"],
            relations=data["relations"],
            constraints=data["constraints"],
        )

        return {"message": "Schema created successfully", "schema_id": schema_id}, 201