import json
import requests
from werkzeug.exceptions import BadRequest
from flask import current_app

import app.config
from app.repositories.token_repository import TokenRepository


class TokenService:
    __token_repository: TokenRepository

    def __init__(self, token_repository):
        self.__token_repository = token_repository

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
                self.__token_repository.create_token(
                    token["text"],
                    token["document_index"],
                    token["pos_tag"],
                    token["sentence_index"],
                    doc_id,
                )
        except:
            raise BadRequest("Tokenization failed")
        return {"tokens": tokens}


token_service = TokenService(TokenRepository())
