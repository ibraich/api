from flask import current_app
from werkzeug.exceptions import BadRequest, Conflict
import requests
import logging

from app.repositories.document_recommendation_repository import (
    DocumentRecommendationRepository,
)
from app.services.mention_services import MentionService, mention_service
from app.services.schema_service import schema_service, SchemaService
from app.services.token_service import token_service, TokenService
from app.services.relation_services import relation_service, RelationService


class DocumentRecommendationService:
    __document_recommendation_repository: DocumentRecommendationRepository
    mention_service: MentionService
    token_service: TokenService
    schema_service: SchemaService
    relation_service: RelationService

    def __init__(
        self,
        document_recommendation_repository,
        mention_service,
        token_service,
        schema_service,
        relation_service,
    ):
        self.__document_recommendation_repository = document_recommendation_repository
        self.mention_service = mention_service
        self.token_service = token_service
        self.schema_service = schema_service
        self.relation_service = relation_service

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
                    schema_constraint.relation_id
                ),
                "schema_mention_head": self.get_schema_mention_dto(
                    schema_constraint.mention_head_id
                ),
                "schema_mention_tail": self.get_schema_mention_dto(
                    schema_constraint.mention_tail_id
                ),
                "is_directed": schema_constraint.isDirected,
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

    def get_relation_recommendation(
        self, document_edit_id, schema_id, content, document_id, params
    ):
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
            schema_id,
            schema_mentions,
            content,
            schema_relations,
            document_edit_id,
            schema_constraints,
            document_id,
        )

        relations_recommendations = (
            self.get_relation_recommendation_from_pipeline_service(
                relation_recommendation_input, params
            )
        )
        logging.debug(f"relations_recommendations: {relations_recommendations}")
        schema_relations_dict = dict()
        for schema_relation in schema_relations:
            schema_relations_dict[schema_relation.tag] = schema_relation.id

        relations_recommendations_with_schema_relation_id = (
            self.add_schema_relation_ids(
                relations_recommendations, schema_relations_dict
            )
        )
        logging.debug(
            f"relations_recommendations_with_schema_relation_id: {relations_recommendations_with_schema_relation_id}"
        )

        schema = self.schema_service.get_schema_by_id(schema_id)
        if schema is None:
            raise BadRequest("Schema not found")
        document_recommendation = self.__document_recommendation_repository.get_document_recommendation_by_document_edit(
            document_edit_id
        )

        if document_recommendation is None:
            raise BadRequest("Document recommendation not found")

        for relation in relations_recommendations_with_schema_relation_id:
            self.schema_service.verify_constraint(
                schema,
                schema_relation_id=relation["schema_relation_id"],
                head_schema_mention_id=relation["head_mention_id"],
                tail_schema_mention_id=relation["tail_mention_id"],
            )

        for relation in relations_recommendations_with_schema_relation_id:
            self.relation_service.create_relation(
                schema_relation_id=relation["schema_relation_id"],
                mention_head_id=relation["head_mention_id"],
                mention_tail_id=relation["tail_mention_id"],
                document_edit_id=document_edit_id,
            )
            relation.isShownRecommendation = True
            relation.document_recommendation_id = document_recommendation.id

    def add_schema_relation_ids(self, relation_recommendations, schema_relations_dict):
        for relation in relation_recommendations:
            relation_tag = relation["tag"]
            if relation_tag in schema_relations_dict:
                relation["schema_relation_id"] = schema_relations_dict[relation_tag]
            else:
                raise BadRequest(f"Relation tag '{relation_tag}' not found in schema.")

        return relation_recommendations

    def get_relation_recommendation_from_pipeline_service(
        self, relation_recommendation_input, params
    ):

        url = current_app.config.get("PIPELINE_URL") + "/steps/relation"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        logging.debug(f"Sending request to pipeline: {url}")
        logging.debug(f"Payload: {relation_recommendation_input}")
        logging.debug(f"Params: {params}")
        response = requests.post(
            url, params=params, json=relation_recommendation_input, headers=headers
        )
        logging.debug(f"Pipeline Response Status: {response.status_code}")
        logging.debug(f"Pipeline Response Text: {response}")
        if response.status_code != 200:
            raise BadRequest(
                "Failed to fetch relation recommendations: " + response.text
            )
        relation_recommendations = response.json()
        logging.debug(f"Pipeline Response JSON: {relation_recommendations}")
        return relation_recommendations

    def get_relation_recommendation_input_dto(
        self,
        schema_id,
        schema_mentions,
        content,
        schema_relations,
        document_edit_id,
        schema_constraints,
        document_id,
    ):
        schema_mention_recommendation_input = (
            self.get_schema_mention_recommendation_input_dto(schema_mentions)
        )
        schema_relation_recommendation_input = (
            self.get_schema_relations_recommendation_input_dto(schema_relations)
        )
        schema_constraints_recommendation_input = (
            self.get_schema_constraints_recommendation_input_dto(schema_constraints)
        )
        mentions_recommendation_input = self.get_mention_recommendation_dto(
            document_edit_id
        )

        return {
            "document_id": str(document_id),
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
        mentions_data = self.mention_service.get_mentions_by_document_edit(
            document_edit_id
        )

        mentions_list = mentions_data.get("mentions", [])

        if not mentions_list:
            raise BadRequest("No mentions found for the given document edit ID.")

        return [
            {
                "id": mention["id"],
                "tag": mention["tag"],
                "tokens": mention["tokens"],
            }
            for mention in mentions_list
        ]


document_recommendation_service = DocumentRecommendationService(
    DocumentRecommendationRepository(),
    mention_service,
    token_service,
    schema_service,
    relation_service,
)
