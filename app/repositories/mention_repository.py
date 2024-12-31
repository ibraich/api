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
                (Mention.document_edit_id == document_edit_id)
                & (
                    Mention.document_recommendation_id.is_(None)
                    | Mention.isShownRecommendation.is_(True)
                )
            )
            .all()
        )

    def get_mention_by_tag(self, tag):
        return self.db_session.query(Mention).filter_by(tag=tag).all()

    def create_mention(
        self,
        tag,
        document_edit_id=None,
        document_recommendation_id=None,
        is_shown_recommendation=False,
    ):
        mention = Mention(
            document_edit_id=document_edit_id,
            tag=tag,
            document_recommendation_id=document_recommendation_id,
            isShownRecommendation=is_shown_recommendation,
        )
        self.store_object(mention)
        return mention

    def get_mentions_by_document_recommendation(self, document_recommendation_id):
        return (
            self.db_session.query(Mention)
            .filter(Mention.document_recommendation_id == document_recommendation_id)
            .all()
        )

    def get_mention_by_id(self, mention_id):
        return self.db_session.query(Mention).filter_by(id=mention_id).first()

    def delete_mention_by_id(self, mention_id):
        mention = self.db_session.query(Mention).get(mention_id)
        if not mention:
            return False
        self.db_session.delete(mention)
        self.db_session.commit()
        return True

    def set_entity_id_to_null(self, entity_id):
        mentions = (
            self.db_session.query(Mention)
            .filter(Mention.entity_id == entity_id)
        ).all()

        for mention in mentions:
            mention.entity_id = None

        self.db_session.commit()
        return len(mentions)

    def get_mentions_by_entity_id(self, entity_id):
        if not isinstance(entity_id, int) or entity_id <= 0:
            raise ValueError("Invalid entity ID. It must be a positive integer.")

        return self.db_session.query(Mention).filter(Mention.entity_id == entity_id).all()

