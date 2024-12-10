from flask import request, jsonify, make_response
from app.services.mention_services import MentionService, mention_service
from app.repositories.mention_repository import MentionRepository
from werkzeug.exceptions import HTTPException, BadRequest
from flask_restx import Resource, Namespace
from app.dtos import mention_input_dto
from app.dtos import mention_output_dto

ns = Namespace("mentions", description="Mention related operations")


@ns.route("/")
class MentionResource(Resource):

    @ns.expect(mention_input_dto)
    @ns.marshal_with(mention_output_dto)
    def post(self):
        mention_service = MentionService(MentionRepository(), MentionRepository())
        return mention_service.create_mentions(mention_input_dto)


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
class MentionQueryResource(Resource):
    def get(self, document_edit_id):
        try:
            if not document_edit_id:
                raise BadRequest("Document Edit ID is required.")

            document_edit_id = int(document_edit_id)

            response, status = mention_service.get_mentions_by_document_edit(
                document_edit_id
            )
            return response, status

        except HTTPException as e:
            return {"message": str(e)}, e.code

        except Exception as e:
            return (
                {"message": "An unexpected error occurred.", "details": str(e)},
                500,
            )
