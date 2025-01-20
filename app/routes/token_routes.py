from werkzeug.exceptions import BadRequest
from flask_restx import Resource, Namespace
from app.dtos import token_output_list_dto
from app.services.token_service import token_service

from app.services.user_service import user_service
from flask_jwt_extended import jwt_required

ns = Namespace("tokens", description="Token related operations")


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "A Document ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class MentionQueryResource(Resource):
    service = token_service
    user_service = user_service

    @jwt_required()
    @ns.doc(description="Get Tokens of document")
    @ns.marshal_with(token_output_list_dto)
    def get(self, document_id):
        if not document_id:
            raise BadRequest("Document Edit ID is required.")

        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)

        tokens = self.service.get_tokens_by_document(document_id)
        if tokens is None:
            return {"tokens": []}
        return {
            "tokens": [
                {
                    "id": token.id,
                    "text": token.text,
                    "document_index": token.document_index,
                    "sentence_index": token.sentence_index,
                    "pos_tag": token.pos_tag,
                }
                for token in tokens
            ]
        }
