from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import NotFound,BadRequest
from flask_restx import Resource, Namespace


from app.db import transactional
from app.services.mention_services import mention_service, MentionService
from app.dtos import (
    mention_output_dto,
    mention_output_list_dto,
    mention_input_dto,
    mention_update_input_dto,
)

ns = Namespace("mentions", description="Mention related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionResource(Resource):
    service = mention_service

    @jwt_required()
    @ns.expect(mention_input_dto)
    @ns.marshal_with(mention_output_dto)
    @jwt_required()
    @transactional
    def post(self):
        return self.service.create_mentions(request.json)


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionQueryResource(Resource):
    service = mention_service

    @jwt_required()
    @ns.doc(description="Get Mentions of document annotation")
    @ns.marshal_with(mention_output_list_dto)
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_mentions_by_document_edit(document_edit_id)
        return response


@ns.route("/<int:mention_id>")
@ns.doc(params={"mention_id": "A Mention ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionDeletionResource(Resource):
    service = mention_service

    @ns.doc(description="Delete a mention and its related relations")
    def delete(self, mention_id):
        response = self.service.delete_mention(mention_id)
        return response

    @jwt_required()
    @ns.expect(mention_update_input_dto)
    @ns.marshal_with(mention_output_dto)
    def patch(self, mention_id):
        data = request.get_json()
        tag = data.get("tag")
        token_ids = data.get("token_ids")
        entity_id = data.get("entity_id")
        response = self.service.update_mention(mention_id, tag, token_ids, entity_id)
        return response
    


@ns.route("/<int:mention_id>/accept")
@ns.doc(params={"mention_id": "A Mention ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Mention not found")
class MentionAcceptResource(Resource):
    @ns.doc(description="Accept a mention by copying it and marking it as processed")
    def post(self, mention_id):
        """
        Accept a mention by copying it to the document edit and setting isShownRecommendation to False.
        """
        document_edit_id = request.args.get("document_edit_id")
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")
        
        return mention_service.accept_mention(mention_id, int(document_edit_id))


@ns.route("/<int:mention_id>/reject")
@ns.doc(params={"mention_id": "A Mention ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Mention not found")
class MentionRejectResource(Resource):
    @ns.doc(description="Reject a mention by marking it as processed")
    def post(self, mention_id):
        """
        Reject a mention by setting isShownRecommendation to False.
        """
        document_edit_id = request.args.get("document_edit_id")
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")
        
        return mention_service.reject_mention(mention_id, int(document_edit_id))

