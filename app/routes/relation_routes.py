from app.services.relation_services import relation_service, RelationService
from werkzeug.exceptions import NotFound,BadRequest
from flask_restx import Namespace, Resource
from app.dtos import relation_output_list_dto, relation_output_dto, relation_input_dto
from flask import request

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
        response = self.service.delete_relation_by_id(relation_id)
        return response, 200


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class RelationCreationResource(Resource):
    service = relation_service

    @ns.doc(description="Create a new relation")
    @ns.marshal_with(relation_output_dto)
    @ns.expect(relation_input_dto)
    def post(self):
        response = self.service.create_relation(request.json)
        return response


@ns.route("/<int:relation_id>/accept")
class RelationAcceptResource(Resource):
    def post(self, relation_id):
        """
        Accept a relation by copying it to the document edit and setting isShownRecommendation to False.
        """
        # Extract document_edit_id from request arguments
        document_edit_id = request.args.get("document_edit_id")
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")
        
        # Call the RelationService to handle the accept logic
        return relation_service.accept_relation(relation_id, int(document_edit_id))

@ns.route("/<int:relation_id>/reject")
class RelationRejectResource(Resource):
    def post(self, relation_id):
        """
        Reject a relation by setting isShownRecommendation to False.
        """
        # Extract document_edit_id from request arguments
        document_edit_id = request.args.get("document_edit_id")
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")
        
        # Call the RelationService to handle the reject logic
        return relation_service.reject_relation(relation_id, int(document_edit_id))