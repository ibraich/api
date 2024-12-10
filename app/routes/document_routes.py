from flask_restx import Namespace, Resource
from flask import request, jsonify
from app.services.document_service import document_service
from werkzeug.exceptions import HTTPException, BadRequest

from ..dtos import fetch_document_output_model

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_service

    @ns.marshal_with(fetch_document_output_model)
    def get(self):
        response = self.service.get_documents_by_user()
        return response
