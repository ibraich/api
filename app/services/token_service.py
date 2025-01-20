import json
import typing

import requests
from werkzeug.exceptions import BadRequest
from flask import current_app

from app.models import Token
from app.repositories.token_repository import TokenRepository
from app.services.user_service import UserService, user_service


class TokenService:
    __token_repository: TokenRepository
    user_service: UserService

    def __init__(self, token_repository, user_service):
        self.__token_repository = token_repository
        self.user_service = user_service

    def tokenize_document(self, doc_id, content):
        url = current_app.config.get("PIPELINE_URL") + "/steps/tokenize"
        request_data = json.dumps({"content": content})
        response = requests.post(
            url=url,
            data=request_data,
            headers={"Content-Type": "application/json"},
        )
        tokens = response.json()
        try:
            for token in tokens:
                self.save_token(
                    token["text"],
                    token["document_index"],
                    token["pos_tag"],
                    token["sentence_index"],
                    doc_id,
                )
        except:
            raise BadRequest("Tokenization failed")
        return {"tokens": tokens}

    def save_token(
        self, text, document_index, pos_tag, sentence_index, doc_id
    ) -> Token:
        return self.__token_repository.create_token(
            text,
            document_index,
            pos_tag,
            sentence_index,
            doc_id,
        )

    def get_tokens_by_document(self, document_id) -> typing.List[Token]:
        return self.__token_repository.get_tokens_by_document(document_id)

    def check_tokens_in_document_edit(self, token_ids, document_edit_id):
        document_tokens = self.__token_repository.get_tokens_by_document_edit(
            document_edit_id
        )
        document_token_ids = [document_token.id for document_token in document_tokens]
        for token_id in token_ids:
            if token_id not in document_token_ids:
                raise BadRequest("Tokens do not belong to this document.")


token_service = TokenService(TokenRepository(), user_service)
