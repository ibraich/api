from flask_restx import Namespace, Resource
from app.services.document_service import document_service
from flask import request
from app.dtos import (
    document_create_output_dto,
    document_create_dto,
    document_output_dto,
)

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_service

    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self):
        response = self.service.get_documents_by_user()
        return response


@ns.route("/upload")
class DocumentUpload(Resource):
    service = document_service

    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(document_create_dto, validate=True)
    @ns.response(201, "Document uploaded successfully.")
    @ns.response(400, "Invalid input.")
    @ns.response(403, "Authorization required.")
    @ns.response(404, "Data not found.")
    @ns.marshal_with(document_create_output_dto)
    def post(self):
        """
        Endpoint for uploading a document to a project.
        """
        data = request.json

        project_id = data.get("project_id")
        file_name = data.get("file_name")
        file_content = data.get("file_content")

        # Upload document via service
        document_details = self.service.upload_document(
            project_id=int(project_id), file_name=file_name, file_content=file_content
        )

        return document_details, 201
