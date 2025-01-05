from app.db import db
from app.models import Token
from app.repositories.base_repository import BaseRepository


class TokenRepository(BaseRepository):
    def create_token(self, text, document_index, pos_tag, sentence_index, document_id):
        token = Token(
            text=text,
            document_index=document_index,
            pos_tag=pos_tag,
            sentence_index=sentence_index,
            document_id=document_id,
        )
        return super().store_object_transactional(token)

    def get_tokens_by_document(self, document_id):
        return db.session.query(Token).filter(Token.document_id == document_id).all()
