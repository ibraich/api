from flask import current_app
from werkzeug.exceptions import BadRequest, Conflict
import requests

from app.repositories.document_recommendation_repository import (
    DocumentRecommendationRepository,
)
from app.services.document_service import DocumentService, document_service
from app.services.mention_services import MentionService, mention_service
from app.services.schema_service import schema_service, SchemaService
from app.services.token_service import token_service, TokenService


class DocumentRecommendationService:
    __document_recommendation_repository: DocumentRecommendationRepository
    mention_service: MentionService
    document_service: DocumentService
    token_service: TokenService
    schema_service: SchemaService

    def __init__(
        self,
        document_recommendation_repository,
        mention_service,
        document_service,
        token_service,
        schema_service,
    ):
        self.__document_recommendation_repository = document_recommendation_repository
        self.mention_service = mention_service
        self.document_service = document_service
        self.token_service = token_service
        self.schema_service = schema_service

    def create_document_recommendation(self, document_id=None, document_edit_id=None):
        return self.__document_recommendation_repository.create_document_recommendation(
            document_id, document_edit_id
        )

    def copy_document_recommendations(
        self,
        document_recommendation_id_source,
        document_edit_id_target,
        document_recommendation_id_target,
    ):
        self.mention_service.copy_mention_recommendations_to_document_edit(
            document_recommendation_id_source,
            document_edit_id_target,
            document_recommendation_id_target,
        )

    def get_mention_recommendation(self, document_id, schema_id):
        # get schema_mention
        schema_mentions = self.schema_service.get_schema_mentions_by_schema(schema_id)
        if schema_mentions is None:
            raise BadRequest("Schema mentions not found")

        # get mention_recommendation from pipeline service and tokens from database
        tokens, mention_recommendations = (
            self.get_mention_recommendation_from_pipeline_service(
                document_id, schema_id, schema_mentions
            )
        )

        # check for duplicate and overlapping tokens
        if not self.no_overlapping_or_duplicate_tokens(mention_recommendations):
            raise Conflict("Overlapping or duplicate mentions found")

        # create id tag dictionary for schema_mention
        schema_mention_dict = dict()
        for schema_mention in schema_mentions:
            schema_mention_dict[schema_mention.tag] = schema_mention.id

        # create dictionary with filtered token ids belonging to a mention along with tag
        filtered_token_ids_and_schema_mention_id = (
            self.filter_tokens_by_schema_recommendations(
                tokens,
                mention_recommendations,
                schema_mention_dict,
            )
        )

        return filtered_token_ids_and_schema_mention_id

    def get_mention_recommendation_from_pipeline_service(
        self, document_id, schema_id, schema_mentions
    ):
        # get request dto for pipeline service
        mention_recommendation_input = self.get_mention_recommendation_input_dto(
            document_id, schema_id, schema_mentions
        )
        # Define the base URL
        url = current_app.config.get("PIPELINE_URL") + "/steps/mention"
        # Define the query parameters
        params = {"model_type": "llm"}
        # Define the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            url, params=params, json=mention_recommendation_input, headers=headers
        )
        mention_recommendations = response.json()
        return mention_recommendation_input["tokens"], mention_recommendations

    def get_mention_recommendation_input_dto(
        self, document_id, schema_id, schema_mentions
    ):
        document = self.document_service.get_document_by_id(document_id)
        if document is None:
            raise BadRequest("Document not found")
        tokens = self.token_service.get_tokens_by_document(document_id)
        if tokens is None:
            raise BadRequest("Tokens not found")
        schema_mention_recommendation_input = (
            self.get_schema_mention_recommendation_input_dto(schema_mentions)
        )

        return {
            "schema": {
                "id": schema_id,
                "schema_mentions": schema_mention_recommendation_input,
            },
            "content": document.content,
            "tokens": tokens,
        }

    def get_schema_mention_recommendation_input_dto(self, schema_mentions):
        return [
            {
                "id": schema_mention.id,
                "tag": schema_mention.tag,
                "description": schema_mention.description,
            }
            for schema_mention in schema_mentions
        ]

    def no_overlapping_or_duplicate_tokens(self, tokens):

        # Sort tokens by their start index
        sorted_tokens = sorted(tokens, key=lambda x: x["startTokenDocumentIndex"])

        # Check for tokens with the same start and end index
        for token in sorted_tokens:
            if token["startTokenDocumentIndex"] == token["endTokenDocumentIndex"]:
                return False  # Token with same start and end index found

        # Iterate through the sorted tokens and check for overlaps
        for i in range(len(sorted_tokens) - 1):
            current_token = sorted_tokens[i]
            next_token = sorted_tokens[i + 1]

            # Check if the current token overlaps with the next token
            if (
                current_token["endTokenDocumentIndex"]
                > next_token["startTokenDocumentIndex"]
            ):
                return False  # Overlap found

        return True  # No overlaps or duplicate tokens found

    def filter_tokens_by_schema_recommendations(
        self, tokens, mention_recommendations, schema_mention_dict
    ):
        result = []

        for mention_recommendations_item in mention_recommendations:
            start = mention_recommendations_item["startTokenDocumentIndex"]
            end = mention_recommendations_item["endTokenDocumentIndex"]
            type_ = mention_recommendations_item["type"]

            # Filter tokens whose document_index is between start and end (inclusive)
            filtered_token_ids = [
                token["id"]
                for token in tokens
                if start <= token["document_index"] <= end
            ]

            # Append the result with the type and filtered tokens
            result.append(
                {
                    "mention_schema_id": schema_mention_dict[type_],
                    "token_ids": filtered_token_ids,
                }
            )

        return result


document_recommendation_service = DocumentRecommendationService(
    DocumentRecommendationRepository(),
    mention_service,
    document_service,
    token_service,
    schema_service,
)
