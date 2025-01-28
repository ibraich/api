from flask_restx import Namespace
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.document_edit_service import document_edit_service
from flask import request
from app.dtos import (
    document_edit_output_dto,
    document_edit_input_dto,
    document_overtake_dto,
    document_edit_output_soft_delete_dto,
    finished_document_edit_output_dto,
    document_edit_model_output_list_dto,
)

ns = Namespace("annotations", description="Document-Annotation related operations")


class DocumentEditBaseRoute(AuthorizedBaseRoute):
    service = document_edit_service


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(DocumentEditBaseRoute):

    @ns.doc(description="Create a new document annotation")
    @ns.marshal_with(document_edit_output_dto)
    @ns.expect(document_edit_input_dto)
    def post(self):
        request_data = request.get_json()

        response = self.service.create_document_edit(
            request_data.get("document_id"),
            request_data.get("model_mention_id"),
            request_data.get("model_entities_id"),
            request_data.get("model_relation_id"),
            request_data.get("model_settings_mention"),
            request_data.get("model_settings_entities"),
            request_data.get("model_settings_relation"),
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
        request_data = request.get_json()

        response = self.service.overtake_document_edit(request_data["document_edit_id"])
        return response


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditDeletionResource(DocumentEditBaseRoute):

    @ns.marshal_with(document_edit_output_soft_delete_dto)
    @ns.doc(description="Soft-delete a DocumentEdit by setting 'active' to False")
    def delete(self, document_edit_id):
        response = self.service.soft_delete_document_edit(document_edit_id)
        return response


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditResource(DocumentEditBaseRoute):

    @ns.marshal_with(
        finished_document_edit_output_dto
    )  # Define the DTO structure for output
    @ns.doc(description="Fetch details of a DocumentEdit by its ID")
    def get(self, document_edit_id):
        response = self.service.get_document_edit_by_id(document_edit_id)
        return response


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
        response = self.service.get_document_edit_model(document_edit_id)
        return response
