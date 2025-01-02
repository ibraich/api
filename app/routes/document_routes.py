from flask_restx import Namespace, Resource
from werkzeug.exceptions import BadRequest

from app.services.document_service import document_service

from app.dtos import document_output_dto

ns = Namespace("documents", description="Document related operations")


@ns.route("/")
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


@ns.route("/project/<int:project_id>")
@ns.doc(params={"project_id": "A Project ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class DocumentProjectRoutes(Resource):
    service = document_service

    @ns.doc(description="Get all documents of project")
    @ns.marshal_with(document_output_dto, as_list=True)
    def get(self, project_id):
        if not project_id:
            raise BadRequest("Project ID is required")
        response = self.service.get_documents_by_project(project_id)
        return response
