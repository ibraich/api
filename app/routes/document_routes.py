from . import document
from flask import request
from app.services.document_service import document_service


@document.route("/", methods=["POST"])
def fetch_documents_for_user():
    service = document_service
    request_data = request.get_json()
    return service.get_documents_by_user(request_data)
