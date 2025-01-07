from app.models import DocumentEdit, DocumentRecommendation
from app.db import db
from app.repositories.base_repository import BaseRepository


class DocumentEditRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def get_user_id(self, id):
        document_edit = db.session.query(DocumentEdit).get(id)
        return document_edit.user_id






class DocumentEditRepository_Recomen_SingleStep(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def get_user_id(self, id):
        document_edit = db.session.query(DocumentEdit).get(id)
        return document_edit.user_id

    def delete_existing_recommendations(self, document_edit_id):
        """Delete all existing recommendations for a document edit."""
        db.session.query(DocumentRecommendation).filter(
            DocumentRecommendation.document_edit_id == document_edit_id
        ).delete()
        db.session.commit()

    def store_new_recommendations(self, document_edit_id, recommendations):
        """Store new recommendations for a document edit."""
        for recommendation in recommendations:
            new_recommendation = DocumentRecommendation(
                document_edit_id=document_edit_id,
                content=recommendation["content"],
                type=recommendation["type"],
            )
            db.session.add(new_recommendation)
        db.session.commit()