from flask_restx import Namespace, Resource
from app.services.document_service import document_service
from flask import request
from werkzeug.exceptions import BadRequest

from app.dtos import document_output_dto

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
@ns.route("/upload")
class DocumentUpload(Resource):
    service = document_service

    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(ns.model('DocumentUpload', {
        'project_id': fields.Integer(required=True, description="ID of the project"),
        'user_id': fields.Integer(required=True, description="ID of the user"),
        'file_name': fields.String(required=True, description="Name of the document"),
        'file_content': fields.String(required=True, description="Content of the document")
    }))
    @ns.response(201, "Document uploaded successfully.")
    @ns.response(400, "Invalid input.")
    @ns.response(403, "Authorization required.")
    @ns.response(404, "Data not found.")
    def post(self):
        """
        Endpoint for uploading a document to a project.
        """
        data = request.json

        project_id = data.get('project_id')
        user_id = data.get('user_id')
        file_name = data.get('file_name')
        file_content = data.get('file_content')

        if not file_name or not file_content.strip():
            raise BadRequest("File name and content are required.")

        # Upload document via service
        document_details = self.service.upload_document(
            user_id=int(user_id),
            project_id=int(project_id),
            file_name=file_name,
            file_content=file_content
        )

        return {"message": "Document uploaded successfully.", "document": document_details}, 201

