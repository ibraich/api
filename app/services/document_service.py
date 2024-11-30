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

    def get_documents_by_user(self, request_data):
        if "user_id" not in request_data:
            response = {"message": "Parameters missing"}
            return response, 400
        user_id = request_data["user_id"]
        # check_auth = self.user_service.check_authentication(user_id)
        # if check_auth[1] == 403:
        #    return check_auth
        projects = self.project_service.get_projects_by_user(user_id)
        documents = self.__get_documents_by_project_list(projects)
        documents_with_edit = []
        if documents is None:
            return []
        for document in documents:
            edit = self.__document_repository.get_document_edit_by_user_and_document(
                user_id, document["id"]
            )
            if edit is None:
                documents_with_edit.append(
                    document | {"document_edit_id": None, "document_edit_type": None}
                )
            else:
                documents_with_edit.append(document | dict(edit._mapping))

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
                documents_of_projects.append(dict(doc._mapping))
        return documents_of_projects


document_service = DocumentService(
    DocumentRepository(), user_service, team_service, project_service
)
