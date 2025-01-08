from app.models import TokenMention
from app.db import db
from app.repositories.base_repository import BaseRepository


class TokenMentionRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def create_token_mention(self, token_id, mention_id):
        token_mention = TokenMention(token_id=token_id, mention_id=mention_id)
        return self.store_object_transactional(token_mention)

    def get_token_mention(self, token_ids, mention_ids):
        return (
            self.db_session.query(TokenMention)
            .filter(
                TokenMention.token_id.in_(token_ids),
                TokenMention.mention_id.in_(mention_ids),
            )
            .all()
        )

    def get_token_mentions_by_mention_id(self, mention_id):
        return (
            self.db_session.query(TokenMention).filter_by(mention_id=mention_id).all()
        )

    def delete_token_mention_by_id(self, token_mention_id):
        token_mention = (
            self.db_session.query(TokenMention).filter_by(id=token_mention_id).first()
        )
        if token_mention:
            self.db_session.delete(token_mention)
            self.db_session.commit()
            return True
        return False
