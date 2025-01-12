from werkzeug.exceptions import BadRequest

from app.repositories import project_document_repository
from app.repositories.project_document_repository import ProjectDocumentRepository


class ProjectDocumentService:
    __project_document_repository: ProjectDocumentRepository()

    def __init__(self, project_document_repository):
        self.__project_document_repository = project_document_repository



    def get_project_by_id(self, project_id):
        project = self.__project_document_repository.get_project_by_id(project_id)
        if project is None:
            raise BadRequest("Project not found")
        return project

    def get_document_by_id(self, document_id):
        return self.__project_document_repository.get_document_by_id(document_id)

project_document_service = ProjectDocumentService(ProjectDocumentRepository())