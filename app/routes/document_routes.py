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
class DocumentUpload(Resource):
    service = document_service

    @ns.doc(description="Upload a document to a specific project.")
    @ns.response(201, "Document uploaded successfully.")
    @ns.response(400, "Invalid input.")
    @ns.response(403, "Authorization required.")
    @ns.response(404, "Data not found.")
    def post(self):
        """
        Endpoint for uploading a document to a project.
        """
        # Parse input data
        file = request.files.get('file')
        project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')  # Assume user_id is sent in the form

        if not file or not project_id or not user_id:
            raise BadRequest("File, project_id, and user_id are required.")

        if file.filename.split('.')[-1].lower() != 'txt':
            raise BadRequest("Only .txt files are allowed.")

        file_content = file.read().decode('utf-8')

        # Upload document via service
        document_details = self.service.upload_document(
            user_id=int(user_id),
            project_id=int(project_id),
            file_name=file.filename,
            file_content=file_content
        )

        return {"message": "Document uploaded successfully.", "document": document_details}, 201
