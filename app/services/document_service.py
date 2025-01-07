from werkzeug.exceptions import NotFound, ServiceUnavailable

from app.repositories.document_repository import DocumentRepository
from app.repositories.document_edit_repository import DocumentEditRepository_Recomen_SingleStep
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








class DocumentService_Recomen_SingleStep:
    def __init__(self, document_edit_repository):
        self.__document_edit_repository = document_edit_repository

    def regenerate_recommendations(self, document_edit_id, step):
        """Regenerate recommendations for a single step (mentions, relations, or entities)."""
        if step not in ["mentions", "relations", "entities"]:
            raise ValueError("Step must be 'mentions', 'relations', or 'entities'.")

        # Check if the document edit exists
        user_id = self.__document_edit_repository.get_user_id(document_edit_id)
        if not user_id:
            raise NotFound("Document edit not found.")

        # Query the recommendation system
        recommendations = self.query_recommendation_system(step, document_edit_id)
        if not recommendations:
            raise ServiceUnavailable("Recommendation system is not available.")

        # Delete existing recommendations and store new ones
        self.__document_edit_repository.delete_existing_recommendations(document_edit_id)
        self.__document_edit_repository.store_new_recommendations(document_edit_id, recommendations)

        return {"status": "success", "recommendations": recommendations}

    def query_recommendation_system(self, step, document_edit_id):
        """Mocked function to query the recommendation system."""
        # This should call an external service or system to get recommendations.
        # Here, we mock a response for simplicity.
        mock_recommendations = [
            {"content": "Sample Mention 1", "type": "mention"},
            {"content": "Sample Mention 2", "type": "mention"},
        ]
        return mock_recommendations
