import requests
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound, InternalServerError,BadRequest
from app.routes.base_routes import AuthorizedBaseRoute
from flask import jsonify, request, current_app
from app.services.document_service import document_service, DocumentService
from app.dtos import (
    document_output_dto,
    document_create_dto,
    document_list_dto,
    document_delete_output_dto,
    heatmap_output_list_dto,
)

ns = Namespace("documents", description="Document related operations")


class DocumentBaseRoute(AuthorizedBaseRoute):
    service: DocumentService = document_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentBaseRoute):

    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_list_dto)
    def get(self):
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

    @ns.doc(description="Get all documents of project")
    @ns.marshal_with(document_list_dto)
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

        document = self.service.get_document_by_id(document_id)
        if not document:
            raise NotFound(f"Document with ID {document_id} not found")

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
                "name": document.name,
            },
            "document_edits": document_edits,
        }

@ns.route("/<int:document_id>/jaccard-index")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Document not found")
class JaccardIndexResource(Resource):
    def post(self, document_id):
        try:
            document = document_service.get_document_by_id(document_id)
            if not document:
                raise NotFound("Document not found")

            document_edits = document_service.get_all_document_edits_by_document(document_id)
            if not document_edits:
                raise NotFound("No edits found for document")

            payload = {"document": document_id, "document_edits": document_edits}
            external_endpoint = current_app.config.get("DIFFERENCE_CALC_URL") + "/jaccard"
            headers = {"accept": "application/json", "Content-Type": "application/json"}

            response = requests.post(external_endpoint, json=payload, headers=headers)
            if response.status_code != 200:
                raise InternalServerError("Jaccard Index calculation failed: " + response.text)

            return jsonify({
                "document": document_id,
                "document_edits": document_edits,
                "jaccard_index": response.json()["jaccard_index"]
            })
        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except NotFound as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500
