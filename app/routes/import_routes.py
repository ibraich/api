from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest

from app.db import transactional
from app.services.import_service import import_service

ns = Namespace("imports", description="Entity related operations")


@ns.route("/documents")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
class Imports(Resource):
    import_service = import_service

    @ns.doc(description="Import documents from other source.")
    @ns.doc(
        params={
            "schema_id": "Used schema for the imported documents.",
            "project_id": "Target project of the documents.",
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

        schema_id = int(request.args.get("schema_id"))
        project_id = int(request.args.get("project_id"))
        source = request.args.get("source")

        if source == "pet":
            return import_service.import_pet_documents(
                import_list, schema_id, project_id, user_id
            )
        else:
            raise BadRequest(f"Invalid source {source}")
