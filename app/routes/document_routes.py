from flask_restx import Namespace, Resource
from werkzeug.exceptions import BadRequest
from app.services.document_service import document_service
from app.services.recommendation_service import RecommendationService
from flask import request, jsonify
from app.dtos import (
    document_create_output_dto,
    document_create_dto,
    document_output_dto,
    document_delete_output_dto,
)
from flask_jwt_extended import jwt_required

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentRoutes(Resource):
    service = document_service

    @jwt_required()
    @ns.doc(description="Get all documents current user has access to")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self):
        response = self.service.get_documents_by_user()
        return response

    @jwt_required()
    @ns.doc(description="Upload a document to a specific project.")
    @ns.expect(document_create_dto, validate=True)
    @ns.response(201, "Document uploaded successfully.")
    @ns.response(400, "Invalid input.")
    @ns.response(403, "Authorization required.")
    @ns.response(404, "Data not found.")
    @ns.marshal_with(document_create_output_dto)
    def post(self):
        """
        Endpoint for uploading a document to a project.
        """
        data = request.json

        project_id = data.get("project_id")
        file_name = data.get("file_name")
        file_content = data.get("file_content")

        # Upload document via service
        document_details = self.service.upload_document(
            project_id=int(project_id), file_name=file_name, file_content=file_content
        )

        return document_details, 201


@ns.route("/project/<int:project_id>")
@ns.doc(params={"project_id": "A Project ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentProjectRoutes(Resource):
    service = document_service

    @jwt_required()
    @ns.doc(description="Get all documents of project")
    @ns.marshal_with(document_output_dto)
    def get(self, project_id):
        if not project_id:
            raise BadRequest("Project ID is required")
        response = self.service.get_documents_by_project(project_id)
        return response


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "Document ID to soft-delete"})
@ns.response(400, "Invalid input")
@ns.response(404, "Document not found")
@ns.response(200, "Document set to inactive successfully")
class DocumentDeletionResource(Resource):
    service = document_service  # an instance of DocumentService

    @jwt_required()
    @ns.marshal_with(document_delete_output_dto)
    @ns.doc(description="Soft-delete a Document by setting 'active' to False")
    def delete(self, document_id):
        response = self.service.soft_delete_document(document_id)
        return response, 200


@ns.route("/recommendations")
@ns.response(400, "Invalid input")
@ns.response(404, "Entity not found")
class RecommendationRoutes(Resource):
    recommendation_service = RecommendationService()

    @ns.doc(description="Retrieve recommendations for a document by document ID")
    def get(self):
        document_id = request.args.get('document_id')
        if not document_id:
            raise BadRequest("Missing document ID in request")
        try:
            recommendations = self.recommendation_service.get_recommendations_for_document(int(document_id))
            return jsonify(recommendations), 200
        except NotFound as e:
            return jsonify({"error": str(e)}), 404
        except BadRequest as e:
            return jsonify({"error": str(e)}), 400

@ns.route("/recommendations/<int:recommendation_id>")
@ns.doc(params={"recommendation_id": "A Recommendation ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Recommendation not found")
class RecommendationManagementRoutes(Resource):
    recommendation_service = RecommendationService()

    @ns.doc(description="Delete a specific recommendation by ID")
    def delete(self, recommendation_id):
        try:
            self.recommendation_service.delete_recommendation_by_id(recommendation_id)
            return jsonify({"message": "Recommendation deleted successfully", "recommendation_id": recommendation_id}), 200
        except NotFound as e:
            return jsonify({"error": str(e)}), 404