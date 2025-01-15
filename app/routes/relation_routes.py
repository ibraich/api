from app.services.relation_services import relation_service, RelationService
from werkzeug.exceptions import NotFound,BadRequest, InternalServerError
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.dtos import (
    relation_output_list_dto,
    relation_output_dto,
    relation_input_dto,
    relation_update_input_dto,
)
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

    @jwt_required()
    @ns.expect(relation_update_input_dto)
    @ns.marshal_with(relation_output_dto)
    @ns.doc(description="Update a Relation by ID")
    def patch(self, relation_id):
        data = request.get_json()
        tag = data.get("tag")
        mention_head_id = data.get("mention_head_id")
        mention_tail_id = data.get("mention_tail_id")
        is_directed = data.get("isDirected")
        response = self.service.update_relation(
            relation_id, tag, mention_head_id, mention_tail_id, is_directed
        )
        return response


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
@ns.doc(params={"relation_id": "A Relation ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Relation not found")
class AcceptRelationResource(Resource):
    service = relation_service

    @jwt_required()
    @ns.doc(description="Accept a relation recommendation.")
    def post(self, relation_id):
        try:
            relation_data = request.json
            relation = self.service.accept_recommendation(relation_data)
            return relation.to_dict(), 200
        except NotFound as e:
            raise NotFound(str(e))
        except Exception:
            raise InternalServerError("An unexpected error occurred.")

@ns.route("/<int:relation_id>/reject")
@ns.doc(params={"relation_id": "A Relation ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Relation not found")
class RejectRelationResource(Resource):
    service = relation_service

    @jwt_required()
    @ns.doc(description="Reject a relation recommendation.")
    def post(self, relation_id):
        try:
            relation_data = request.json
            relation = self.service.reject_recommendation(relation_data)
            return relation.to_dict(), 200
        except NotFound as e:
            raise NotFound(str(e))
        except Exception:
            raise InternalServerError("An unexpected error occurred.")

