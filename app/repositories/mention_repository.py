from app.models import Mention
from app.db import db
from app.repositories.base_repository import BaseRepository


class MentionRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def get_mentions_by_document_edit(self, document_edit_id):
        return (
            self.db_session.query(Mention)
            .filter(
                (Mention.document_edit_id == document_edit_id) &
                (
                        Mention.document_recommendation_id.is_(None) |
                        Mention.isShownRecommendation.is_(True)
                )
            )
            .all()
        )
