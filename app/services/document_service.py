from werkzeug.exceptions import NotFound

from app.repositories.document_repository import DocumentRepository
from app.services.user_service import UserService, user_service
from app.services.team_service import TeamService, team_service
from app.services.project_service import ProjectService, project_service


class DocumentService:
    __document_repository: DocumentRepository
    user_service: UserService
    team_service: TeamService
    project_service: ProjectService

    def __init__(
        self, document_repository, user_service, team_service, project_service
    ):
        self.__document_repository = document_repository
        self.user_service = user_service
        self.team_service = team_service
        self.project_service = project_service

    def get_documents_by_project(self, project_id):
        return self.__document_repository.get_documents_by_project(project_id)

    def get_documents_by_user(self, user_id):
        self.user_service.check_authentication(user_id)
        projects = self.project_service.get_projects_by_user(user_id)
        documents = self.__get_documents_by_project_list(projects)
        documents_with_edit = []
        if documents is None:
            raise NotFound("No documents available.")
        for document in documents:
            edit = self.__document_repository.get_document_edit_by_user_and_document(
                user_id, document["id"]
            )
            if edit is None:
                documents_with_edit.append(
                    document | {"document_edit_id": None, "document_edit_type": None}
                )
            else:
                documents_with_edit.append(
                    document
                    | {
                        "document_edit_id": edit.id,
                        "document_edit_type": edit.type,
                    }
                )
        if not documents_with_edit:
            raise NotFound("No documents available.")
        return documents_with_edit, 200

    def get_documents_by_team(self, team_id):
        projects = self.project_service.get_projects_by_team(team_id)
        return self.__get_documents_by_project_list(projects)

    def __get_documents_by_project_list(self, projects):
        documents_of_projects = []
        if projects is None:
            return []
        for project in projects:
            docs = self.get_documents_by_project(project.id)
            if docs is None:
                continue
            for doc in docs:
                documents_of_projects.append(
                    {
                        "content": doc.content,
                        "id": doc.id,
                        "name": doc.name,
                        "project_id": doc.project_id,
                        "project_name": doc.project_name,
                        "type": doc.type,
                    }
                )
        return documents_of_projects


document_service = DocumentService(
    DocumentRepository(), user_service, team_service, project_service
)
