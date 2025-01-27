from app.models import DocumentRecommendation
from app.repositories.base_repository import BaseRepository


class DocumentRecommendationRepository(BaseRepository):

    def create_document_recommendation(self, document_id, document_edit_id=None):
        document_recommendation = DocumentRecommendation(
            document_id=document_id,
            document_edit_id=document_edit_id,
            state_id=1,
            documentEditHash="",
        )
        return super().store_object(document_recommendation)
