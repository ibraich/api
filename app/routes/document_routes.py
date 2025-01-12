from flask_restx import Namespace, Resource
from werkzeug.exceptions import BadRequest
from app.services.document_service import document_service
from app.services.user_service import user_service
from flask import request
from app.dtos import (
    document_create_output_dto,
    document_create_dto,
    document_output_dto,
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
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self, project_id):
        if not project_id:
            raise BadRequest("Project ID is required")
        response = self.service.get_documents_by_project(project_id)
        return response


@ns.route("/<int:document_id>/regenerate-recommendations")
@ns.response(200, "Success")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
class RegenerateRecommendations(Resource):
    def post(self, document_id):
        """(Re-)generate recommendations for a specific step of a document."""
        step = request.args.get("step")
        if step not in ["mentions", "relations", "entities"]:
            return {"error": "Invalid step provided."}, 400

        try:
            # Fetch the logged-in user's ID
            user_id = user_service.get_logged_in_user_id()
            response = document_service.regenerate_recommendations(document_id, step, user_id)
            return response, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "An unexpected error occurred."}, 500


@ns.route("/<int:document_id>")
@ns.doc(params={"document_id": "Document ID to soft-delete"})
@ns.response(400, "Invalid input")
@ns.response(404, "Document not found")
@ns.response(200, "Document set to inactive successfully")
class DocumentDeletionResource(Resource):
    service = document_service  # An instance of DocumentService

    @jwt_required()
    @ns.marshal_with(document_delete_output_dto)
    @ns.doc(description="Soft-delete a Document by setting 'active' to False")
    def delete(self, document_id):
        """Soft-delete a document by setting its 'active' flag to False."""
        try:
            success = self.service.soft_delete_document(document_id)
            if not success:
                return {"error": "Document not found."}, 404
            return {"message": "Document set to inactive successfully."}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "An unexpected error occurred."}, 500