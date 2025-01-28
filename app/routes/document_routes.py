import requests
from flask_restx import Namespace
from werkzeug.exceptions import BadRequest, NotFound
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.document_service import document_service
from flask import request
from app.dtos import (
    document_create_output_dto,
    document_create_dto,
    document_output_dto,
    document_delete_output_dto,
    heatmap_output_list_dto,
)

ns = Namespace("documents", description="Document related operations")


class DocumentBaseRoute(AuthorizedBaseRoute):
    service = document_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentBaseRoute):

    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self):
        response = self.service.get_documents_by_user()
        return response

    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(document_create_dto)
    @ns.response(201, "Document uploaded successfully.")
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


@ns.route("/project/<int:project_id>")
@ns.doc(params={"project_id": "A Project ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentProjectRoutes(DocumentBaseRoute):

    @ns.doc(description="Get all documents of project")
    @ns.marshal_with(document_output_dto)
    def get(self, project_id):
        if not project_id:
            raise BadRequest("Project ID is required")
        response = self.service.get_documents_by_project(project_id)
        return response


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "Document ID to soft-delete"})
@ns.response(404, "Document not found")
@ns.response(200, "Document set to inactive successfully")
class DocumentDeletionResource(DocumentBaseRoute):

    @ns.marshal_with(document_delete_output_dto)
    @ns.doc(description="Soft-delete a Document by setting 'active' to False")
    def delete(self, document_id):
        response = self.service.soft_delete_document(document_id)
        return response


@ns.route("/<int:document_id>/heatmap")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
@ns.response(500, "Internal server error")
class DocumentEditsSenderResource(DocumentBaseRoute):

    @ns.marshal_with(heatmap_output_list_dto)
    @ns.doc(
        description="Send all DocumentEdit data for a specific Document ID to an external service"
    )
    def get(self, document_id):
        document_edits = self.service.get_all_document_edits_with_user_by_document(
            document_id
        )
        if not document_edits:
            raise NotFound(f"No DocumentEdits found for Document ID {document_id}")

        document = self.service.get_document_by_id(document_id)
        if not document:
            raise NotFound(f"Document with ID {document_id} not found")

        transformed_edits = self.service.get_all_structured_document_edits_by_document(
            document_id
        )

        external_endpoint = (
            "http://annotation_difference_calc:8443/difference-calc/heatmap"
        )

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            external_endpoint, json=transformed_edits, headers=headers
        )

        if response.status_code != 200:
            return {
                "message": f"Failed to send data: {response.text}"
            }, response.status_code
        return {
            "items": response.json(),
            "document": {
                "id": document_id,
                "name": document.name,
            },
            "document_edits": document_edits,
        }, 200
