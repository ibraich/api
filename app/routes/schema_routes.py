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

@app.route('/schemas', methods=['POST'])
def create_schema():
 
    try:
        data = request.get_json()
        team_id = data.get("team_id")
        mentions = data.get("schema_mentions")
        relations = data.get("schema_relations")
        constraints = data.get("schema_constraints")

        if not all([team_id, mentions, relations, constraints]):
            raise BadRequest("Missing required fields.")

        schema_service.create_schema(team_id, mentions, relations, constraints)
        return jsonify({"message": "Schema created successfully."}), 201

    except Conflict as e:
        return jsonify({"error": str(e)}), 409
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error."}), 500