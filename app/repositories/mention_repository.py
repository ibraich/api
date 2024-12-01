from app.models import Mention
from app.db import db

class MentionRepository:
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def get_mentions_by_document(self, document_id):
        return (
            self.db_session.query(Mention)
            .filter_by(document_recommendation_id=document_id)
            .all()
        )