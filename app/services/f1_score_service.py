from flask import current_app
from werkzeug.exceptions import NotFound, BadRequest
import requests

from app.services.document_edit_service import (
    DocumentEditService,
    document_edit_service,
)


class F1ScoreService:
    document_edit_service: DocumentEditService

    def __init__(
        self,
        document_edit_service: DocumentEditService,
    ):
        self.document_edit_service = document_edit_service

    def get_f1_score(self, actual_document_edit_id, predicted_document_edit_id):
        f1_score_request_dto = self.__get_f1_score_request_dto(
            actual_document_edit_id, predicted_document_edit_id
        )
        # Define the base URL
        url = current_app.config.get("PIPELINE_URL") + "/f1-score"
        # Define the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(url, json=f1_score_request_dto, headers=headers)
        if response.status_code != 200:
            raise BadRequest("Failed to fetch f1 score: " + response.text)
        f1_score = response.json()
        return f1_score

    def __get_f1_score_request_dto(
        self, actual_document_edit_id, predicted_document_edit_id
    ):
        actual_document_edit_dto = self.document_edit_service.get_document_edit_by_id(
            actual_document_edit_id
        )
        predicted_document_edit_dto = (
            self.document_edit_service.get_document_edit_by_id(
                predicted_document_edit_id
            )
        )

        if actual_document_edit_dto is None or predicted_document_edit_dto is None:
            raise NotFound("document edit not found")

        return self.__map_actual_and_predicted_to_model(
            actual_document_edit_dto, predicted_document_edit_dto
        )

    def __map_actual_and_predicted_to_model(self, actual_dto, predicted_dto):
        # Map the actual DTO
        actual_mapped = {
            "document": self.__map_document(actual_dto["document"]),
            "mentions": [
                self.__map_mention(mention) for mention in actual_dto["mentions"]
            ],
            "relations": [
                self.__map_relation(relation) for relation in actual_dto["relations"]
            ],
        }

        # Map the predicted DTO
        predicted_mapped = {
            "document": self.__map_document(predicted_dto["document"]),
            "mentions": [
                self.__map_mention(mention) for mention in predicted_dto["mentions"]
            ],
            "relations": [
                self.__map_relation(relation) for relation in predicted_dto["relations"]
            ],
        }

        # Return the final structure
        return {
            "actual": actual_mapped,
            "predicted": predicted_mapped,
        }

    def __map_document(self, document):
        """Helper function to map a document."""

        return {
            "id": document["id"],
            "tokens": [
                {
                    "id": token["id"],
                    "text": token["text"],
                    "document_index": token["document_index"],
                    "sentence_index": token["sentence_index"],
                    "pos_tag": token["pos_tag"],
                }
                for token in document["tokens"]
            ],
        }

    def __map_mention(self, mention):
        """Helper function to map a mention."""
        return {
            "tag": mention["tag"],
            "tokens": [
                {
                    "id": token["id"],
                    "text": token["text"],
                    "document_index": token["document_index"],
                    "sentence_index": token["sentence_index"],
                    "pos_tag": token["pos_tag"],
                }
                for token in mention["tokens"]
            ],
            "entity": {"id": mention["entity_id"]},
        }

    def __map_relation(self, relation):
        """Helper function to map a relation."""
        return {
            "tag": relation["tag"],
            "mention_head": self.__map_mention(relation["head_mention"]),
            "mention_tail": self.__map_mention(relation["tail_mention"]),
        }


f1_score_service = F1ScoreService(document_edit_service)
