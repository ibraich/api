from werkzeug.exceptions import NotFound, BadRequest
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_edit_repository import DocumentEditRepository
from app.services.mention_services import MentionService
from app.services.schema_service import SchemaService
from app.repositories.document_recommendation_repository import DocumentRecommendationRepository

class RecommendationService:
    def __init__(self, document_repository: DocumentRepository,
                 document_edit_repository: DocumentEditRepository,
                 mention_service: MentionService,
                 schema_service: SchemaService,
                 recommendation_repository: DocumentRecommendationRepository):
        self.document_repository = document_repository
        self.document_edit_repository = document_edit_repository
        self.mention_service = mention_service
        self.schema_service = schema_service
        self.recommendation_repository = recommendation_repository

    def get_recommendations_for_document(self, document_id: int):
        # Fetch document edit ID
        document_edit = self.document_edit_repository.get_by_document_id(document_id)
        if not document_edit:
            raise NotFound(f"No document edit found for document ID {document_id}")

        # Fetch mentions and schema
        mentions = self.mention_service.get_mentions_by_document_edit_id(document_edit.id)
        schema = self.schema_service.get_schema_by_document_edit_id(document_edit.id)

        if not mentions or not schema:
            raise BadRequest("Mentions or schema missing for the document edit ID")

        # Generate recommendations
        recommendations = self._generate_recommendations(mentions, schema)

        # Store recommendations
        for recommendation in recommendations:
            self.recommendation_repository.create(recommendation)

        return recommendations

    def delete_recommendation_by_id(self, recommendation_id: int):
        recommendation = self.recommendation_repository.get_by_id(recommendation_id)
        if not recommendation:
            raise NotFound(f"Recommendation ID {recommendation_id} does not exist")

        self.recommendation_repository.delete(recommendation_id)

    def _generate_recommendations(self, mentions, schema):
        # Placeholder logic for generating recommendations
        return [
            {"mention_id": mention.id, "schema_id": schema.id, "recommendation": "Sample Recommendation"}
            for mention in mentions
        ]
