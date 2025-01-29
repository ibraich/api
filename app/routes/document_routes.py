from flask_restx import Namespace
from werkzeug.exceptions import BadRequest
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.document_service import document_service, DocumentService
from flask import request
from app.dtos import (
    document_create_output_dto,
    document_create_dto,
    document_output_dto,
    document_delete_output_dto,
)

ns = Namespace("documents", description="Document related operations")


class DocumentBaseRoute(AuthorizedBaseRoute):
    service: DocumentService = document_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentBaseRoute):

    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self):
        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.get_documents_by_user(user_id)
        return response

    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(document_create_dto)
    @ns.response(404, "Data not found.")
    @ns.marshal_with(
        document_create_output_dto,
        description="Document uploaded successfully.",
    )
    def post(self):
        """
        Endpoint for uploading a document to a project.
        """
        data = request.json

        project_id = data.get("project_id")
        file_name = data.get("file_name")
        file_content = data.get("file_content")

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_project_accessible(user_id, project_id)

        # Upload document via service
        document_details = self.service.upload_document(
            user_id,
            project_id=project_id,
            file_name=file_name,
            file_content=file_content,
        )
        return document_details


@ns.route("/project/<int:project_id>")
@ns.doc(params={"project_id": "A Project ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentProjectRoutes(DocumentBaseRoute):

    @ns.doc(description="Get all documents of project")
    @ns.marshal_with(document_output_dto)
    def get(self, project_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_project_accessible(user_id, project_id)

        response = self.service.get_documents_by_project(user_id, project_id)
        return response


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "Document ID to soft-delete"})
@ns.response(404, "Document not found")
@ns.response(200, "Document set to inactive successfully")
class DocumentDeletionResource(DocumentBaseRoute):

    @ns.marshal_with(document_delete_output_dto)
    @ns.doc(description="Soft-delete a Document by setting 'active' to False")
    def delete(self, document_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        response = self.service.soft_delete_document(document_id)
        return response
