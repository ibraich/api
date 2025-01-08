from flask import request
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from app.services.mention_services import mention_service, MentionService
from app.dtos import mention_output_dto, mention_output_list_dto, mention_input_dto

ns = Namespace("mentions", description="Mention related operations")

mention_service = MentionService(...)

@ns.route("/")
@ns.route("/<int:mention_id>/accept")
@ns.route("/<int:mention_id>/delete")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionResource(Resource):
    service = mention_service

    @ns.expect(mention_input_dto)
    @ns.marshal_with(mention_output_dto)
    def post(self):
        return self.service.create_mentions(request.json)
        
    def post1(self, mention_id):
        user_id = request.headers.get("User-ID")
        if not user_id:
            raise BadRequest("User-ID header is required.")
        return mention_service.accept_mention(mention_id, int(user_id))

@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionQueryResource(Resource):
    service = mention_service

    @ns.doc(description="Get Mentions of document annotation")
    @ns.marshal_with(mention_output_list_dto)
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_mentions_by_document_edit(document_edit_id)
        return response


class MentionDeleteResource(Resource):
    def post(self, mention_id):
        user_id = request.headers.get("User-ID")
        if not user_id:
            raise BadRequest("User-ID header is required.")
        return mention_service.reject_mention(mention_id, int(user_id))