from app.services.relation_services import relation_service, RelationService
from werkzeug.exceptions import BadRequest
from flask_restx import Namespace, Resource
from app.dtos import relation_output_list_dto
from flask import jsonify, request

ns = Namespace("relations", description="Relation related operations")
relation_service = RelationService(...)

@ns.route("/<int:document_edit_id>")
@ns.route("/<int:relation_id>/accept")
@ns.route("/<int:relation_id>/delete")
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


class RelationAcceptResource(Resource):
    def post(self, relation_id):
        user_id = request.headers.get("User-ID")
        if not user_id:
            raise BadRequest("User-ID header is required.")
        return relation_service.accept_relation(relation_id, int(user_id))



class RelationDeleteResource(Resource):
    def post(self, relation_id):
        user_id = request.headers.get("User-ID")
        if not user_id:
            raise BadRequest("User-ID header is required.")
        return relation_service.reject_relation(relation_id, int(user_id))
    

@ns.route("/<int:relation_id>/accept")
class AcceptRelationResource(Resource):
    def post(self, relation_id):
        """
        Accepts a recommendation for a relation by its ID.
        """
        user_id = request.headers.get("X-User-ID")  # Simuliert die Benutzer-ID aus den Headern
        if not user_id:
            return jsonify({"error": "User ID missing in request headers"}), 400

        with db.session as session:
            try:
                result = relation_service.accept_relation(session, relation_id, int(user_id))
                return jsonify(result), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400


@ns.route("/<int:relation_id>/reject")
class RejectRelationResource(Resource):
    def post(self, relation_id):
        """
        Rejects a recommendation for a relation by its ID.
        """
        user_id = request.headers.get("X-User-ID")  # Simuliert die Benutzer-ID aus den Headern
        if not user_id:
            return jsonify({"error": "User ID missing in request headers"}), 400

        with db.session as session:
            try:
                result = relation_service.reject_relation(session, relation_id, int(user_id))
                return jsonify(result), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400