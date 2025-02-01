from flask import current_app
from werkzeug.exceptions import BadRequest, Conflict
import requests

from app.repositories.document_recommendation_repository import (
    DocumentRecommendationRepository,
)
from app.services.mention_services import MentionService, mention_service
from app.services.schema_service import schema_service, SchemaService
from app.services.token_service import token_service, TokenService


class DocumentRecommendationService:
    __document_recommendation_repository: DocumentRecommendationRepository
    mention_service: MentionService
    token_service: TokenService
    schema_service: SchemaService

    def __init__(
        self,
        document_recommendation_repository,
        mention_service,
        token_service,
        schema_service,
    ):
        self.__document_recommendation_repository = document_recommendation_repository
        self.mention_service = mention_service
        self.token_service = token_service
        self.schema_service = schema_service

    def create_document_recommendation(self, document_id=None, document_edit_id=None):
        return self.__document_recommendation_repository.create_document_recommendation(
            document_id, document_edit_id
        )

    def get_mention_recommendation(self, document_id, schema_id, content, params):
        # get schema_mention
        schema_mentions = self.schema_service.get_schema_mentions_by_schema(schema_id)
        if schema_mentions is None:
            raise BadRequest("Schema mentions not found")

        tokens = self.token_service.get_tokens_by_document(document_id)["tokens"]
        if tokens is None:
            raise BadRequest("Tokens not found")

        mention_recommendation_input = self.get_mention_recommendation_input_dto(
            tokens, schema_id, schema_mentions, content, document_id
        )

        # get mention_recommendation from pipeline service
        mention_recommendations = self.get_mention_recommendation_from_pipeline_service(
            mention_recommendation_input, params=params
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
        self, mention_recommendation_input, params
    ):
        # get request dto for pipeline service

        # Define the base URL
        url = current_app.config.get("PIPELINE_URL") + "/steps/mention"
        # Define the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            url, params=params, json=mention_recommendation_input, headers=headers
        )
        if response.status_code != 200:
            raise BadRequest("Failed to fetch recommendations: " + response.text)
        mention_recommendations = response.json()
        return mention_recommendations

    def get_mention_recommendation_input_dto(
        self, tokens, schema_id, schema_mentions, content, document_id
    ):
        schema_mention_recommendation_input = (
            self.get_schema_mention_recommendation_input_dto(schema_mentions)
        )

        return {
            "document_id": str(document_id),
            "schema": {
                "id": schema_id,
                "schema_mentions": schema_mention_recommendation_input,
            },
            "content": content,
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

    def get_schema_relations_recommendation_input_dto(self, schema_relations):
        return [
            {
                "id": schema_relation.id,
                "tag": schema_relation.tag,
                "description": schema_relation.description,
            }
            for schema_relation in schema_relations
        ]

    def get_schema_constraints_recommendation_input_dto(self, schema_constraints):
        return [
            {
                "schema_relation": self.get_schema_relation_dto(
                    schema_constraint.schema_relation_id
                ),
                "schema_mention_head": self.get_schema_mention_dto(
                    schema_constraint.schema_mention_head
                ),
                "schema_mention_tail": self.get_schema_mention_dto(
                    schema_constraint.schema_mention_tail
                ),
                "is_directed": schema_constraint.is_directed,
            }
            for schema_constraint in schema_constraints
        ]

    def no_overlapping_or_duplicate_tokens(self, tokens):

        # Sort tokens by their start index
        sorted_tokens = sorted(tokens, key=lambda x: x["startTokenDocumentIndex"])

        # Check for tokens with the same start and end index
        for token in sorted_tokens:
            if token["startTokenDocumentIndex"] > token["endTokenDocumentIndex"]:
                return False  # Token with higher start than end index found

        # Iterate through the sorted tokens and check for overlaps
        for i in range(len(sorted_tokens) - 1):
            current_token = sorted_tokens[i]
            next_token = sorted_tokens[i + 1]

            # Check if the current token overlaps with the next token
            if (
                current_token["endTokenDocumentIndex"]
                >= next_token["startTokenDocumentIndex"]
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

    def get_relation_recommendation(self, schema_id, content, document_edit_id, params):
        schema_mentions = self.schema_service.get_schema_mentions_by_schema(schema_id)
        if schema_mentions is None:
            raise BadRequest("Schema mentions not found")

        schema_relations = self.schema_service.get_schema_relations_by_schema(schema_id)
        if schema_relations is None:
            raise BadRequest("Schema relations not found")

        schema_constraints = self.schema_service.get_schema_constraints_by_schema(
            schema_id
        )
        if schema_constraints is None:
            raise BadRequest("Schema constraints not found")

        relation_recommendation_input = self.get_relation_recommendation_input_dto(
            schema_id, schema_mentions, content, schema_relations, document_edit_id
        )

        relations_recommendations = (
            self.get_relation_recommendation_from_pipeline_service(
                relation_recommendation_input, params
            )
        )

    def get_relation_recommendation_from_pipeline_service(
        self, relation_recommendation_input, params
    ):
        url = current_app.config.get("PIPELINE_URL") + "/steps/relation"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(
            url, params=params, json=relation_recommendation_input, headers=headers
        )
        if response.status_code != 200:
            raise BadRequest(
                "Failed to fetch relation recommendations: " + response.text
            )
        relation_recommendations = response.json()
        return relation_recommendations

    def get_relation_recommendation_input_dto(
        self,
        schema_id,
        schema_mentions,
        schema_relations,
        content,
        document_edit_id,
    ):
        schema_mention_recommendation_input = (
            self.get_schema_mention_recommendation_input_dto(schema_mentions)
        )
        schema_relation_recommendation_input = (
            self.get_schema_relations_recommendation_input_dto(schema_relations)
        )
        schema_constraints_recommendation_input = (
            self.get_schema_constraints_recommendation_input_dto(schema_relations)
        )
        mentions_recommendation_input = self.get_mention_recommendation_dto(
            document_edit_id
        )

        return {
            "schema": {
                "id": schema_id,
                "schema_mentions": schema_mention_recommendation_input,
                "schema_relations": schema_relation_recommendation_input,
                "schema_constraints": schema_constraints_recommendation_input,
            },
            "content": content,
            "mentions": mentions_recommendation_input,
        }

    def get_schema_relation_dto(self, schema_relation_id):
        schema_relation = self.schema_service.get_schema_relation_by_id(
            schema_relation_id
        )
        return {
            "id": schema_relation.id,
            "tag": schema_relation.tag,
            "description": schema_relation.description,
        }

    def get_schema_mention_dto(self, schema_mention_id):
        schema_mention = self.schema_service.get_schema_mention_by_id(schema_mention_id)

        return {
            "id": schema_mention.id,
            "tag": schema_mention.tag,
            "description": schema_mention.description,
        }

    def get_mention_recommendation_dto(self, document_edit_id):
        mentions = self.mention_service.get_mentions_by_document_edit(document_edit_id)
        return {
            "id": mentions.id,
            "tag": mentions.tag,
            "tokens": mentions.tokens,
        }


document_recommendation_service = DocumentRecommendationService(
    DocumentRecommendationRepository(),
    mention_service,
    token_service,
    schema_service,
)
