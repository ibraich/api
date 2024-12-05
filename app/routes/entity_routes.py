from flask import request, jsonify
from . import entities
from app.services.entity_service import EntityService
from app.repositories.entity_repository import EntityRepository
from werkzeug.exceptions import HTTPException, BadRequest


@entities.route("/<document_edit_id>", methods=["GET"])
def get_entities_by_document_edit(document_edit_id):
    entity_service = EntityService(EntityRepository())

    try:
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        if not document_edit_id.isdigit():
            raise BadRequest("Document Edit ID must be a valid integer.")

        document_edit_id = int(document_edit_id)

        response, status = entity_service.get_entities_by_document_edit(
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

