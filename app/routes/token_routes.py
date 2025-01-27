from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace


from app.dtos import token_output_list_dto
from app.services.token_service import token_service
from flask_jwt_extended import jwt_required

ns = Namespace("tokens", description="Token related operations")


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionQueryResource(Resource):
    service = token_service

    @ns.doc(description="Get Tokens of document")
    @ns.marshal_with(token_output_list_dto)
    @jwt_required()
    def get(self, document_id):
        if not document_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_tokens_by_document(document_id)
        return response
