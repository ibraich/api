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
        self.repository = DocumentRepository()
        self.document_repository = document_repository

    def get_documents_by_project(self, user_id, project_id):
        response = self.get_documents_by_user(user_id)
        documents = response["documents"]
        filtered_documents = [
            document
            for document in documents
            if document["project"]["id"] == project_id
        ]
        return {"documents": filtered_documents}

    def get_documents_by_user(self, user_id):
        documents = self.__document_repository.get_documents_by_user(user_id)
        if not documents:
            raise NotFound("No documents found")
        document_list = [self.__map_document_to_output_dto(doc) for doc in documents]
        return {"documents": document_list}

    def upload_document(self, user_id, project_id, file_name, file_content):
        # Validate file content
        if not file_name or not file_content.strip():
            raise ValueError("Invalid file content or file name.")

        # Store the document
        document = self.__document_repository.create_document(
            name=file_name, content=file_content, project_id=project_id, user_id=user_id
        )

        # Tokenize document
        self.token_service.tokenize_document(document.id, document.content)
        document_output = self.get_document_by_id(document.id)
        return self.__map_document_to_output_dto(document_output)

    def get_document_by_id(self, document_id):
        return self.__document_repository.get_document_by_id_without_edit(document_id)

    def save_document(
        self, name: str, content: str, project_id: int, creator_id: int, state_id: int
    ):
        return self.__document_repository.save(
            name, content, project_id, creator_id, state_id
        )

    def soft_delete_document(self, document_id: int):
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

    def get_all_structured_document_edits_by_document(self, document_id):
        document_edits = self.__document_repository.get_all_document_edits_by_document(
            document_id
        )
        if not document_edits:
            raise NotFound("No DocumentEdits found for document ID")

        transformed_edits = [
            self.document_edit_service.get_document_edit_by_id(document_edit.id)
            for document_edit in document_edits
        ]

        return transformed_edits

    def get_all_document_edits_with_user_by_document(self, document_id):
        document_edits = (
            self.__document_repository.get_all_document_edits_with_user_by_document(
                document_id
            )
        )
        if not document_edits:
            raise NotFound("No DocumentEdits found for document ID")

        processed_edits = [
            {
                "id": document_id,
                "user": {
                    "id": edit.user_id,
                    "email": edit.user_email,
                    "username": edit.user_username,
                },
            }
            for edit in document_edits
        ]

        return processed_edits


    def __map_document_to_output_dto(self, doc):
        return {
            "id": doc.id,
            "content": doc.content,
            "name": doc.name,
            "state": {
                "id": doc.document_state_id,
                "type": doc.document_state_type,
            },
            "project": {
                "id": doc.project_id,
                "name": doc.project_name,
            },
            "schema": {
                "id": doc.schema_id,
                "name": doc.schema_name,
            },
            "team": {
                "id": doc.team_id,
                "name": doc.team_name,
            },
            "document_edit": {
                "id": doc.document_edit_id,
                "state": doc.document_edit_state,
            },
            "creator": {
                "id": doc.creator_id,
                "username": doc.username,
                "email": doc.email,
            },
        }
    def get_document_by_id(self, document_id):
        document = self.document_repository.fetch_document_by_id(document_id)
        if not document:
            raise NotFound("Document not found")
        return document

    def get_all_document_edits_by_document(self, document_id):
        edits = self.document_repository.fetch_document_edits(document_id)
        if not edits:
            raise NotFound("No DocumentEdits found")
        return [{"id": edit.id, "content": edit.content} for edit in edits]


document_service = DocumentService(
    DocumentRepository(),
    user_service,
    team_service,
    token_service,
    document_edit_service,
)
