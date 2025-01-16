from app.models import Mention, TokenMention
from app.db import db, Session
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session



class MentionRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session
        self.db = db

    def get_mentions_with_tokens_by_document_edit(self, document_edit_id):
        results = (
            self.db_session.query(
                Mention.id.label("mention_id"),
                Mention.tag,
                Mention.isShownRecommendation,
                Mention.document_edit_id,
                Mention.document_recommendation_id,
                Mention.entity_id,
                TokenMention.token_id,
            )
            .outerjoin(TokenMention, Mention.id == TokenMention.mention_id)
            .filter(
                (Mention.document_edit_id == document_edit_id)
                & (
                    Mention.document_recommendation_id.is_(None)
                    | Mention.isShownRecommendation.is_(True)
                )
            )
            .all()
        )

        return results

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
        return self.store_object_transactional(mention)

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
            self.db_session.query(Mention).filter(Mention.entity_id == entity_id)
        ).all()

        for mention in mentions:
            mention.entity_id = None

        self.db_session.commit()
        return len(mentions)

    def add_to_entity(self, entity_id: int, mention_id: int):
        Session.query(Mention).filter_by(id=mention_id).update({"entity_id": entity_id})

    def save_mention(
        self,
    ):
        self.db_session.commit()

    def get_mentions_by_entity_id(self, entity_id):
        if not isinstance(entity_id, int) or entity_id <= 0:
            raise ValueError("Invalid entity ID. It must be a positive integer.")

        return (
            self.db_session.query(Mention).filter(Mention.entity_id == entity_id).all()
        )

    def update_mention(self, mention_id, tag, entity_id):
        mention = self.get_mention_by_id(mention_id)
        if tag:
            mention.tag = tag
        if entity_id:
            mention.entity_id = entity_id
        elif entity_id == 0:
            mention.entity_id = None
        super().store_object(mention)
        return mention

    def update_is_shown_recommendation(self, mention_id, value):
        """
        Aktualisiert den isShownRecommendation-Wert eines Mention-Eintrags.
        """
        mention = self.db_session.query(Mention).filter_by(id=mention_id).first()
        if mention:
            mention.isShownRecommendation = value
            self.db_session.commit()
        return mention

