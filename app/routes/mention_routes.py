from flask import request
from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from app.dtos import mention_input_dto
from app.dtos import mention_output_dto
from app.services.mention_services import mention_service

ns = Namespace("mentions", description="Mention related operations")


@ns.route("/")
class MentionResource(Resource):
    service = mention_service

    @ns.expect(mention_input_dto)
    @ns.marshal_with(mention_output_dto)
    def post(self):
        return self.service.create_mentions(request.json)


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
class MentionQueryResource(Resource):
    service = mention_service

    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        document_edit_id = int(document_edit_id)

        response = self.service.get_mentions_by_document_edit(document_edit_id)
        return response
