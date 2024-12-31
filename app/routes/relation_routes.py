from app.services.relation_services import relation_service
from werkzeug.exceptions import BadRequest
from flask_restx import Namespace, Resource
from app.dtos import relation_output_list_dto

ns = Namespace("relations", description="Relation related operations")


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class RelationQueryResource(Resource):
    service = relation_service

    @ns.doc(description="Get Relations of document annotation")
    @ns.marshal_with(relation_output_list_dto)
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_relations_by_document_edit(document_edit_id)
        return response

@ns.route("/<int:relation_id>")
@ns.doc(params={"relation_id": "A Relation ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class RelationDeleteResource(Resource):
    service = relation_service

    @ns.doc(description="Delete a Relation by ID")
    def delete(self, relation_id):
        response = self.service.delete_relation(relation_id)
        return response, 200
