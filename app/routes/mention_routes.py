from flask import request, jsonify
from . import mentions
from app.services.mention_services import MentionService
from app.repositories.mention_repository import MentionRepository
from werkzeug.exceptions import HTTPException, BadRequest


@mentions.route("/<document_edit_id>", methods=["GET"])
def get_mentions_by_document_edit(document_edit_id):
    mention_service = MentionService(MentionRepository())

    try:
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        if not document_edit_id.isdigit():
            raise BadRequest("Document Edit ID must be a valid integer.")

        document_edit_id = int(document_edit_id)

        response, status = mention_service.get_mentions_by_document_edit(
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
