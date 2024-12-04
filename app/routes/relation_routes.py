from flask import request, jsonify
from . import relations
from app.services.relation_services import RelationService
from app.repositories.relation_repository import RelationRepository
from werkzeug.exceptions import HTTPException, BadRequest


@relations.route("/<document_edit_id>", methods=["GET"])
def get_relations_by_document(document_edit_id):
    relation_service = RelationService(RelationRepository())
    try:
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        if not document_edit_id.isdigit():
            raise BadRequest("Document Edit ID must be a valid integer.")

        document_edit_id = int(document_edit_id)

        response, status = relation_service.get_relations_by_document_edit(
            document_edit_id
        )
        return jsonify(response), status

    except HTTPException as e:
        return jsonify({"message": str(e)}), e.code

    except Exception as e:
        return (
            jsonify({"message": "An unexpected error occurred.", "details": str(e)}),
            500,
        )
