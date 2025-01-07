from flask_restx import Namespace, Resource
from app.repositories.document_edit_repository import DocumentEditRepository_Recomen_SingleStep
from app.services.document_service import document_service, DocumentService
from werkzeug.exceptions import BadRequest

from app.dtos import document_output_dto

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
@ns.route("/document-edit/<int:document_edit_id>/regenerate/<string:step>")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_service

    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self):
        response = self.service.get_documents_by_user()
        return response





document_service = DocumentService(DocumentEditRepository_Recomen_SingleStep())
class RecommendationRegeneration_Recomen_SingleStep(Resource):
    def post(self, document_edit_id, step):
        """Regenerate recommendations for a single step."""
        try:
            response = document_service.regenerate_recommendations(document_edit_id, step)
            return {"message": "Recommendations regenerated successfully.", "data": response}, 200
        except ValueError as e:
            raise BadRequest(str(e))