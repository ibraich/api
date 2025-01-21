from werkzeug.exceptions import NotFound, BadRequest

from app.repositories.document_repository import DocumentRepository
from app.services.document_edit_service import (
    document_edit_service,
    DocumentEditService,
)
from app.services.user_service import UserService, user_service
from app.services.token_service import TokenService, token_service
from app.services.team_service import TeamService, team_service


class DocumentService:
    __document_repository: DocumentRepository
    user_service: UserService
    team_service: TeamService
    token_service: TokenService
    document_edit_service: DocumentEditService

    def __init__(
        self,
        document_repository,
        user_service,
        team_service,
        token_service,
        document_edit_service,
    ):
        self.__document_repository = document_repository
        self.user_service = user_service
        self.team_service = team_service
        self.token_service = token_service
        self.document_edit_service = document_edit_service

    def get_documents_by_project(self, project_id):
        response = self.get_documents_by_user()
        documents = response["documents"]
        filtered_documents = [
            document
            for document in documents
            if document["project"]["project_id"] == project_id
        ]
        return {"documents": filtered_documents}

    def get_documents_by_user(self):
        user_id = self.user_service.get_logged_in_user_id()
        documents = self.__document_repository.get_documents_by_user(user_id)
        if not documents:
            raise NotFound("No documents found")
        document_list = [
            {
                "id": doc.id,
                "content": doc.content,
                "name": doc.name,
                "project": {
                    "project_id": doc.project_id,
                    "project_name": doc.project_name,
                },
                "schema": {
                    "schema_id": doc.schema_id,
                    "schema_name": doc.schema_name,
                },
                "team": {
                    "team_id": doc.team_id,
                    "team_name": doc.team_name,
                },
                "document_edit": {
                    "document_edit_id": doc.document_edit_id,
                    "document_edit_state": doc.document_edit_state,
                },
            }
            for doc in documents
        ]
        return {"documents": document_list}

    def upload_document(self, project_id, file_name, file_content):

        user_id = self.user_service.get_logged_in_user_id()

        # Validate that the user has access to the project
        self.user_service.check_user_project_accessible(user_id, project_id)

        # Validate file content
        if not file_name or not file_content.strip():
            raise ValueError("Invalid file content or file name.")

        # Store the document
        document = self.__document_repository.create_document(
            name=file_name, content=file_content, project_id=project_id, user_id=user_id
        )

        # Tokenize document
        self.token_service.tokenize_document(document.id, document.content)

        return {
            "id": document.id,
            "name": document.name,
            "project_id": document.project_id,
            "content": document.content,
            "state_id": document.state_id,
            "creator_id": document.creator_id,
        }

    def get_document_by_id(self, document_id):
        return self.__document_repository.get_document_by_id(document_id)

    def save_document(
        self, name: str, content: str, project_id: int, creator_id: int, state_id: int
    ):
        return self.__document_repository.save(
            name, content, project_id, creator_id, state_id
        )

    def soft_delete_document(self, document_id: int):
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_accessible(user_id, document_id)
        if not isinstance(document_id, int) or document_id <= 0:
            raise BadRequest("Invalid document ID. Must be a positive integer.")

        success = self.__document_repository.soft_delete_document(document_id)
        if not success:
            raise NotFound("Document not found or already inactive.")

        self.document_edit_service.soft_delete_edits_for_document(document_id)

        return {"message": "Document set to inactive successfully."}

    def bulk_soft_delete_documents_by_project_id(self, project_id):
        document_ids = (
            self.__document_repository.bulk_soft_delete_documents_by_project_id(
                project_id
            )
        )

        if document_ids:
            self.document_edit_service.bulk_soft_delete_edits_for_documents(
                document_ids
            )


document_service = DocumentService(
    DocumentRepository(),
    user_service,
    team_service,
    token_service,
    document_edit_service,
)
