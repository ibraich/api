from flask_restx import Namespace, Resource
from app.services.document_service import document_service, DocumentService_Reccomendation_a_r
from werkzeug.exceptions import BadRequest
from app.dtos import document_output_dto

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
@ns.route("/recommendations/<int:recommendation_id>")
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








ns = Namespace("documents", description="Document-related operations")

document_service = DocumentService_Reccomendation_a_r(DocumentService_Reccomendation_a_r())
class RecommendationRoutes(Resource):
    def put(self, recommendation_id):
        """Accept or reject a recommendation."""
        action = ns.payload.get("action")
        if action not in ["accept", "reject"]:
            raise BadRequest("Action must be 'accept' or 'reject'.")
        
        if action == "accept":
            response = document_service.accept_recommendation(recommendation_id)
            return {"message": "Recommendation accepted successfully.", "data": response}, 200
        else:
            response = document_service.reject_recommendation(recommendation_id)
            return {"message": "Recommendation rejected successfully.", "data": response}, 200
        