from app.models import Token, DocumentEdit
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
        return super().store_object(token)

    def get_tokens_by_document(self, document_id):
        return (
            self.get_session()
            .query(Token)
            .filter(Token.document_id == document_id)
            .all()
        )

    def get_tokens_by_document_edit(self, document_edit_id):
        return (
            self.get_session()
            .query(Token)
            .select_from(DocumentEdit)
            .join(Token, Token.document_id == DocumentEdit.document_id)
            .filter(DocumentEdit.id == document_edit_id)
            .all()
        )
