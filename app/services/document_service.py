from werkzeug.exceptions import NotFound

from app.repositories.document_repository import DocumentRepository
from app.services.user_service import UserService, user_service
from app.services.team_service import TeamService, team_service
from app.services.project_service import ProjectService, project_service


class DocumentService:
    __document_repository: DocumentRepository
    user_service: UserService

    def __init__(self, document_repository, user_service):
        self.__document_repository = document_repository
        self.user_service = user_service
        self.team_service = team_service
        self.project_service = project_service

    def get_documents_by_project(self, project_id):
        return self.__document_repository.get_documents_by_project(project_id)

    def get_documents_by_user(self):
        user_id = self.user_service.get_logged_in_user_id()
        documents = self.__document_repository.get_documents_by_user(user_id)
        if not documents:
            raise NotFound("No documents found")
        document_list = [
            {
                "content": doc.content,
                "id": doc.id,
                "name": doc.name,
                "project_id": doc.project_id,
                "project_name": doc.project_name,
                "schema_id": doc.schema_id,
                "team_name": doc.team_name,
                "team_id": doc.team_id,
                "document_edit_id": doc.document_edit_id,
                "document_edit_state": doc.document_edit_state,
            }
            for doc in documents
        ]
        return document_list


document_service = DocumentService(DocumentRepository(), user_service)
