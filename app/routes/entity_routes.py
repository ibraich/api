from flask_restx import Namespace, Resource
from app.services.entity_service import entity_service
from werkzeug.exceptions import BadRequest
from app.dtos import (
    entity_output_list_dto,
    entity_input_dto,
    entity_output_dto,
)
from flask import request
from flask_jwt_extended import jwt_required

ns = Namespace("entities", description="Entity related operations")


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityQueryResource(Resource):
    service = entity_service

    @ns.doc(description="Get Entities of document annotation")
    @ns.marshal_with(entity_output_list_dto)
    @jwt_required()
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_entities_by_document_edit(document_edit_id)
        return response


@ns.route("/<int:entity_id>")
@ns.doc(params={"entity_id": "An Entity ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityDeletionResource(Resource):
    service = entity_service

    @ns.doc(description="Delete an entity")
    @jwt_required()
    def delete(self, entity_id):
        response = self.service.delete_entity(entity_id)
        return response


@ns.route("")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityCreationResource(Resource):
    service = entity_service

    @ns.doc(description="Create a new entity")
    @ns.marshal_with(entity_output_dto)
    @ns.expect(entity_input_dto)
    @jwt_required()
    def post(self):
        response = self.service.create_entity(request.json)
        return response
