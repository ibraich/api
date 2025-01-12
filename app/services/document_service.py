from werkzeug.exceptions import NotFound

from app.repositories.document_repository import DocumentRepository
from app.services.user_service import UserService, user_service
from app.services.token_service import TokenService, token_service
from app.services.project_service import ProjectService, project_service
from app.services.token_service import TeamService, team_service


class DocumentService:
    __document_repository: DocumentRepository
    user_service: UserService
    team_service: TeamService
    project_service: ProjectService
    token_service: TokenService

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
        self.project_service = project_service
        self.token_service = token_service

    def get_documents_by_project(self, project_id):
        documents = self.get_documents_by_user()
        return [
            document for document in documents if document["project_id"] == project_id
        ]

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

    def upload_document(self, project_id, file_name, file_content):
        """
        Args:
            project_id (int): ID of the project to upload the document to.
            file_name (str): Name of the file.
            file_content (str): Content of the file.

        Raises:
            NotFound: If the project or team is not found, or the user is not authorized.
            ValueError: If the file content is invalid or file name is missing.

        Returns:
            dict: Details of the uploaded document.
        """

        user_id = self.user_service.get_logged_in_user_id()

        # Validate that the user belongs to the team that owns the project
        project = self.project_service.get_project_by_id(project_id)
        if not project:
            raise NotFound("Project not found.")

        team_id = project.team_id
        self.user_service.check_user_in_team(user_id, team_id)

        # Validate file content
        if not file_name or not file_content.strip():
            raise ValueError("Invalid file content or file name.")

        # Store the document
        document = self.__document_repository.create_document(
            name=file_name, content=file_content, project_id=project_id, user_id=user_id
        )
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
    


    def regenerate_recommendations(self, document_id, step, user_id):
        """(Re-)generate recommendations for a specific step of a document."""
        # Validate user permissions for the document
        document = self.__document_repository.get_by_id(document_id)
        if not document or document.user_id != user_id:
            raise ValueError("Document does not belong to the logged-in user or does not exist.")
        
        # Query recommendation system (mocked for now)
        recommendations = self.query_recommendation_system(document_id, step)
        if not recommendations:
            raise ValueError("Failed to fetch recommendations from the recommendation system.")

        # Delete existing mentions or relations
        self.__document_repository.delete_existing_mentions_or_relations(document_id, step)

        # Store new mentions or relations
        self.__document_repository.store_new_mentions_or_relations(document_id, recommendations, step)

        return {"message": f"{step.capitalize()} recommendations regenerated successfully."}

    def query_recommendation_system(self, document_id, step):
        """Mock querying the recommendation system."""
        # Simulate response from a recommendation system
        return [
            {"type": step, "content": f"Recommendation for {step} in document {document_id}"},
        ]


document_service = DocumentService(
    DocumentRepository(), user_service, team_service, project_service, token_service
)
