from flask_restx import Namespace
from app.routes.base_routes import AuthorizedBaseRoute
from app.services.entity_service import entity_service
from werkzeug.exceptions import BadRequest
from app.dtos import (
    entity_output_list_dto,
    entity_input_dto,
    entity_output_dto,
)
from flask import request

ns = Namespace("entities", description="Entity related operations")


class EntityBaseRoute(AuthorizedBaseRoute):
    service = entity_service


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityQueryResource(EntityBaseRoute):

    @ns.doc(description="Get Entities of document annotation")
    @ns.marshal_with(entity_output_list_dto)
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_entities_by_document_edit(document_edit_id)
        return response


@ns.route("/<int:entity_id>")
@ns.doc(params={"entity_id": "An Entity ID"})
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityDeletionResource(EntityBaseRoute):

    @ns.doc(description="Delete an entity")
    def delete(self, entity_id):
        response = self.service.delete_entity(entity_id)
        return response


@ns.route("")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityCreationResource(EntityBaseRoute):

    @ns.doc(description="Create a new entity")
    @ns.marshal_with(entity_output_dto)
    @ns.expect(entity_input_dto)
    def post(self):
        response = self.service.create_entity(request.json)
        return response
