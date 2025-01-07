from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest

from app.db import transactional
from app.services.import_service import import_service

ns = Namespace("imports", description="Import data from different sources")


@ns.route("/documents")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
class Imports(Resource):
    import_service = import_service

    @ns.doc(description="Import documents from other source.")
    @ns.doc(
        params={
            "project_id": "Target project of the documents. (Defines the target schema)",
            "source": "Data source type. Only option: 'pet'",
        }
    )
    @jwt_required()
    @transactional
    def post(self):
        """
        Import documents from different data sources.
        Currently, only a list of PET documents is supported
        """
        user_id = int(get_jwt_identity())
        import_list = request.get_json()

        project_id = int(request.args.get("project_id"))
        source = request.args.get("source")

        if source == "pet":
            return import_service.import_pet_documents(import_list, project_id, user_id)
        else:
            raise BadRequest(f"Invalid source {source}")


@ns.route("/schema")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
class Imports(Resource):
    import_service = import_service

    @ns.doc(description="Import schema.")
    @ns.doc(
        params={
            "team_id": "Target team of the schema.",
        }
    )
    @jwt_required()
    @transactional
    def post(self):
        user_id = int(get_jwt_identity())
        import_schema = request.get_json()

        team_id = int(request.args.get("team_id"))

        # TODO Backend Team: Check if user is part of the team

        return import_service.import_schema(import_schema, team_id)
