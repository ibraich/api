from app.models import Mention, Relation
from app.db import db
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session



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

    def create_mention(self, document_edit_id, tag):
        mention = Mention(
            document_edit_id=document_edit_id,
            tag=tag,
        )
        self.store_object(mention)
        return mention


    def set_is_shown_recommendation_false(self, mention_id):
        mention = self.db_session.query(Mention).filter_by(id=mention_id).first()
        if mention:
            mention.is_shown_recommendation = False
            self.db_session.commit()
        return mention

    def copy_to_document_edit(self, mention, user_id):
        new_mention = Mention(
            content=mention.content,
            document_edit_id=mention.document_edit_id,
            user_id=user_id,
            is_shown_recommendation=False,
            document_recommendation_id=None,
        )
        self.db_session.add(new_mention)
        self.db_session.commit()
        return new_mention
    
    def update_is_shown_recommendation(session, mention_id, is_shown: bool):
     mention = session.query(Mention).filter(Mention.id == mention_id).one_or_none()
     if mention:
        mention.is_shown_recommendation = is_shown
        session.commit()
        return mention
     return None
    
    def create_mention_in_edit(session, mention_data):
        new_mention = Mention(**mention_data)
        session.add(new_mention)
        session.commit()
        return new_mention

   
    