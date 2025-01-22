from werkzeug.exceptions import BadRequest, Conflict
from flask_restx import Resource, Namespace
from app.dtos import schema_output_dto, schema_output_list_dto
from app.services.schema_service import schema_service, SchemaService
from flask_jwt_extended import jwt_required
from flask import Flask, request, jsonify
from app.services.user_service import UserService
from app.repositories.schema_repository import SchemaRepository
from app.models import SchemaMention, SchemaRelation, SchemaConstraint, Schema


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

@jwt_required()
@ns.doc(description="Create a new schema")
@ns.response(201, "Schema created successfully")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
class SchemaResource(Resource):
    def post(self):
        """
        POST /schemas
        Creates a new schema with mentions, relations, and constraints.

        :return: JSON response with the created schema.
        """
        user_id = self.schema_service._SchemaService__user_service.get_logged_in_user_id()
        data = request.json

        # Validate input
        required_fields = ["team_id", "schema_data"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        schema_data = data["schema_data"]
        mentions = data.get("mentions", [])
        relations = data.get("relations", [])
        constraints = data.get("constraints", [])

        # Create schema using service
        schema = self.schema_service.create_schema(user_id, schema_data, mentions, relations, constraints)

        return {
            "id": schema.id,
            "name": schema.name,
            "team_id": schema.team_id,
            "mentions": [mention.to_dict() for mention in schema.mentions],
            "relations": [relation.to_dict() for relation in schema.relations],
            "constraints": [constraint.to_dict() for constraint in schema.constraints],
        }, 201