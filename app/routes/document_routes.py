from . import document
from flask import request, jsonify
from app.services.document_service import document_service
from werkzeug.exceptions import HTTPException, BadRequest


@document.route("/", methods=["POST"])
def fetch_documents_for_user():
    service = document_service

    try:
        request_data = request.get_json()
        if "user_id" not in request_data:
            raise BadRequest("User ID is required.")
        user_id = request_data["user_id"]
        try:
            user_id = int(user_id)
        except:
            raise BadRequest("User ID must be a valid integer.")
        response, status = service.get_documents_by_user(user_id)
        return jsonify(response), status

    except HTTPException as e:
        return {"message": str(e)}, e.code
    except Exception as e:
        return (
            {"message": "An unexpected error occurred.", "details": str(e)},
            500,
        )
