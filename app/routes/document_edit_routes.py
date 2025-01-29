from flask_restx import Namespace
import requests
from werkzeug.exceptions import NotFound, BadRequest
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.document_edit_service import (
    document_edit_service,
    DocumentEditService,
)
from flask import request, current_app
from app.dtos import (
    document_edit_output_dto,
    document_edit_input_dto,
    document_overtake_dto,
    document_edit_output_soft_delete_dto,
    finished_document_edit_output_dto,
    heatmap_output_list_dto,
    document_edit_model_output_list_dto,
)

ns = Namespace("annotations", description="Document-Annotation related operations")


class DocumentEditBaseRoute(AuthorizedBaseRoute):
    service: DocumentEditService = document_edit_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentEditBaseRoute):

    @ns.doc(description="Create a new document annotation")
    @ns.marshal_with(document_edit_output_dto)
    @ns.expect(document_edit_input_dto)
    def post(self):
        data = request.get_json()

        document_id = (data.get("document_id"),)
        user_id = self.user_service.get_logged_in_user_id()

        self.user_service.check_user_document_accessible(user_id, document_id)

        response = self.service.create_document_edit(
            user_id,
            document_id,
            data.get("model_mention_id"),
            data.get("model_entities_id"),
            data.get("model_relation_id"),
            data.get("model_settings_mention"),
            data.get("model_settings_entities"),
            data.get("model_settings_relation"),
        )
        return response


@ns.route("/overtake")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentEditBaseRoute):

    @ns.doc(description="overtake another user annotation")
    @ns.marshal_with(document_edit_output_dto)
    @ns.expect(document_overtake_dto)
    def post(self):
        data = request.json
        user_id = self.user_service.get_logged_in_user_id()

        response = self.service.overtake_document_edit(
            user_id, data.get("document_edit_id")
        )
        return response


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditDeletionResource(DocumentEditBaseRoute):

    @ns.marshal_with(document_edit_output_soft_delete_dto)
    @ns.doc(description="Soft-delete a DocumentEdit by setting 'active' to False")
    def delete(self, document_edit_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(user_id, document_edit_id)

        response = self.service.soft_delete_document_edit(document_edit_id)
        return response


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditResource(DocumentEditBaseRoute):

    @ns.marshal_with(finished_document_edit_output_dto)
    @ns.doc(description="Fetch details of a DocumentEdit by its ID")
    def get(self, document_edit_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(user_id, document_edit_id)

        response = self.service.get_document_edit_by_id(document_edit_id)
        return response


@ns.route("/<int:document_id>/heatmap")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
@ns.response(500, "Internal server error")
class DocumentEditsSenderResource(DocumentEditBaseRoute):

    @ns.doc(
        description="Send all DocumentEdit data for a specific Document ID to an external service"
    )
    @ns.marshal_with(heatmap_output_list_dto)
    def post(self, document_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        transformed_edits = self.service.get_all_document_edits_by_document(document_id)

        external_endpoint = current_app.config.get("DIFFERENCE_CALC_URL") + "/heatmap"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            external_endpoint, json=transformed_edits, headers=headers
        )

        # Handle response from the external endpoint
        if response.status_code != 200:
            raise BadRequest("Heatmap calculation failed: " + response.text)

        return {"items": response.json()}


@ns.route("/<int:document_edit_id>/model")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditResource(DocumentEditBaseRoute):

    @ns.marshal_with(document_edit_model_output_list_dto)
    @ns.doc(
        description="Fetch details of the models used in Recommendations for DocumentEdit"
    )
    def get(self, document_edit_id):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(user_id, document_edit_id)

        response = self.service.get_document_edit_model(document_edit_id)
        return response
