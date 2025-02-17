import requests
from flask_restx import Namespace
from werkzeug.exceptions import NotFound, InternalServerError
from flask import request, current_app
from app.services.document_service import document_service, DocumentService
from app.dtos import (
    document_output_dto,
    document_create_dto,
    document_list_dto,
    document_delete_output_dto,
    heatmap_output_list_dto,
    jaccard_output_dto,
    document_state_update_dto,
)
from app.routes.base_routes import AuthorizedBaseRoute

ns = Namespace("documents", description="Document related operations")


class DocumentBaseRoute(AuthorizedBaseRoute):
    service: DocumentService = document_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentBaseRoute):

    @ns.marshal_with(document_list_dto)
    def get(self):
        """
        Fetch all documents the user has access to.
        Documents also contain list of users which have annotated this document.
        """
        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.get_documents_by_user(user_id)
        return response

    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(document_create_dto)
    @ns.response(404, "Data not found.")
    @ns.marshal_with(
        document_output_dto,
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

    @ns.marshal_with(document_list_dto)
    def get(self, project_id):
        """
        Fetch all documents of a project the user has access to.
        Documents also contain list of users which have annotated this document.
        """
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


@ns.route("/<int:document_id>/heatmap")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditsSenderResource(DocumentBaseRoute):

    @ns.marshal_with(heatmap_output_list_dto)
    @ns.doc(
        description="Send all DocumentEdit data for a specific Document ID to an external service"
    )
    def get(self, document_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        document_edits = self.service.get_all_document_edits_with_user_by_document(
            document_id
        )
        if not document_edits:
            raise NotFound(f"No DocumentEdits found for Document ID {document_id}")

        document = self.service.get_document_by_id(document_id, user_id)

        transformed_edits = self.service.get_all_structured_document_edits_by_document(
            document_id
        )

        external_endpoint = current_app.config.get("DIFFERENCE_CALC_URL") + "/heatmap"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            external_endpoint, json=transformed_edits, headers=headers
        )

        if response.status_code != 200:
            raise InternalServerError("Heatmap calculation failed: " + response.text)

        return {
            "items": response.json(),
            "document": {
                "id": document_id,
                "name": document["name"],
            },
            "document_edits": document_edits,
        }


@ns.route("/<int:document_id>/jaccard-index")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Document not found")
class JaccardIndexResource(DocumentBaseRoute):

    @ns.marshal_with(jaccard_output_dto)
    @ns.doc(
        description="Send all DocumentEdit data for a specific Document ID to an external service"
    )
    def get(self, document_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        document = self.service.get_document_by_id(document_id, user_id)
        if not document:
            raise NotFound(f"Document with ID {document_id} not found")

        document_edits = self.service.get_all_document_edits_with_user_by_document(
            document_id
        )
        if not document_edits:
            raise NotFound(f"No DocumentEdits found for Document ID {document_id}")

        transformed_edits = self.service.get_all_structured_document_edits_by_document(
            document_id
        )

        external_endpoint = (
            current_app.config.get("DIFFERENCE_CALC_URL") + "/jaccard-index"
        )
        headers = {"accept": "application/json", "Content-Type": "application/json"}

        response = requests.post(
            external_endpoint, json=transformed_edits, headers=headers
        )
        if response.status_code != 200:
            raise InternalServerError(
                "Jaccard Index calculation failed: " + response.text
            )

        return {
            "document": {
                "id": document_id,
                "name": document["name"],
            },
            "document_edits": document_edits,
            "result": response.json(),
        }


@ns.response(403, "Authorization required")
@ns.route("/<int:document_id>/state")
@ns.doc(params={"document_id": "A Document ID"})
class DocumentStateResource(DocumentBaseRoute):

    @ns.expect(document_state_update_dto)
    @ns.marshal_with(document_output_dto)
    def put(self, document_id):
        """
        Update the state of a document.
        """
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        data = request.get_json()
        new_state_id = data.get("state_id")

        updated_document = self.service.change_document_state(
            document_id, new_state_id, user_id
        )

        return updated_document
