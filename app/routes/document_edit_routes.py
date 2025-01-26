import requests
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound, BadRequest

from app.db import transactional
from app.services.document_edit_service import document_edit_service
from flask import request
from app.dtos import (
    document_edit_output_dto,
    document_edit_input_dto,
    document_overtake_dto,
    document_edit_output_soft_delete_dto,
    finished_document_edit_output_dto,
    heatmap_output_list_dto,
    document_edit_model_output_list_dto,
)
from flask_jwt_extended import jwt_required

ns = Namespace("annotations", description="Document-Annotation related operations")


@ns.route("")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.doc(description="Create a new document annotation")
    @ns.marshal_with(document_edit_output_dto)
    @ns.expect(document_edit_input_dto, validate=True)
    @transactional
    def post(self):
        request_data = request.get_json()
        document_id = request_data.get("document_id")
        model_mention = request_data.get("model_mention_id")
        model_entities = request_data.get("model_entities_id")
        model_relation = request_data.get("model_relation_id")
        model_settings_mention = request_data.get("model_settings_mention")
        model_settings_entities = request_data.get("model_settings_entities")
        model_settings_relation = request_data.get("model_settings_relation")
        response = self.service.create_document_edit(
            document_id,
            model_mention,
            model_entities,
            model_relation,
            model_settings_mention,
            model_settings_entities,
            model_settings_relation,
        )
        return response


@ns.route("/overtake")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.doc(description="overtake another user annotation")
    @ns.marshal_with(document_edit_output_dto)
    @ns.expect(document_overtake_dto, validate=True)
    @transactional
    def post(self):
        request_data = request.get_json()

        response = self.service.overtake_document_edit(request_data["document_edit_id"])
        return response



@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditDeletionResource(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.marshal_with(document_edit_output_soft_delete_dto)
    @ns.doc(description="Soft-delete a DocumentEdit by setting 'active' to False")
    def delete(self, document_edit_id):
        response = self.service.soft_delete_document_edit(document_edit_id)
        return response


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditResource(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.marshal_with(
        finished_document_edit_output_dto
    )  # Define the DTO structure for output
    @ns.doc(description="Fetch details of a DocumentEdit by its ID")
    def get(self, document_edit_id):
        response = self.service.get_document_edit_by_id(document_edit_id)
        return response


@ns.route("/<int:document_id>/heatmap")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
@ns.response(500, "Internal server error")
class DocumentEditsSenderResource(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.doc(
        description="Send all DocumentEdit data for a specific Document ID to an external service"
    )
    @ns.expect(finished_document_edit_output_dto, validate=False)
    @ns.marshal_with(heatmap_output_list_dto)
    def post(self, document_id):
        try:
            transformed_edits = self.service.get_all_document_edits_by_document(
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

            # Handle response from the external endpoint
            if response.status_code != 200:
                return {
                    "message": f"Failed to send data: {response.text}"
                }, response.status_code

            return {"items": response.json()}, 200

        except NotFound as e:
            return {"message": str(e)}, 404
        except BadRequest as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": f"An unexpected error occurred: {str(e)}"}, 500
          
@ns.route("/<int:document_edit_id>/model")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentEditResource(Resource):
    service = document_edit_service

    @jwt_required()
    @ns.marshal_with(document_edit_model_output_list_dto)
    @ns.doc(
        description="Fetch details of the models used in Recommendations for DocumentEdit"
    )
    def get(self, document_edit_id):
        response = self.service.get_document_edit_model(document_edit_id)
        return response
