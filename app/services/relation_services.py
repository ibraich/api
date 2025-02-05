from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.models import Relation
from app.repositories.relation_repository import RelationRepository
from app.services.relation_mention_service import (
    relation_mention_service,
    RelationMentionService,
)
from app.services.schema_service import schema_service, SchemaService
from app.services.user_service import user_service, UserService
from app.services.mention_services import mention_service, MentionService


class RelationService:
    __relation_repository: RelationRepository
    user_service: UserService
    schema_service: SchemaService
    mention_service: MentionService
    relation_mention_service: RelationMentionService

    def __init__(
        self,
        relation_repository,
        user_service,
        schema_service,
        mention_service: MentionService,
        relation_mention_service,
    ):
        self.__relation_repository = relation_repository
        self.user_service = user_service
        self.schema_service = schema_service
        self.mention_service = mention_service
        self.relation_mention_service = relation_mention_service

    def get_relations_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        mentions_data = self.mention_service.get_mentions_by_document_edit(
            document_edit_id
        )
        mentions_dict = {
            mention["id"]: mention for mention in mentions_data["mentions"]
        }

        relations = self.__relation_repository.get_relations_by_document_edit(
            document_edit_id
        )

        transformed_relations = []
        for relation in relations:
            head_mention = mentions_dict.get(relation.mention_head_id)
            tail_mention = mentions_dict.get(relation.mention_tail_id)

            if not head_mention or not tail_mention:
                continue

            transformed_relations.append(
                {
                    "id": relation.id,
                    "isDirected": relation.isDirected,
                    "isShownRecommendation": relation.isShownRecommendation,
                    "document_edit_id": relation.document_edit_id,
                    "document_recommendation_id": relation.document_recommendation_id,
                    "schema_relation": {
                        "id": relation.schema_relation_id,
                        "tag": relation.tag,
                        "description": relation.description,
                        "schema_id": relation.schema_id,
                    },
                    "tag": relation.tag,
                    "head_mention": head_mention,
                    "tail_mention": tail_mention,
                }
            )

        return {"relations": transformed_relations}

    def save_relation_in_edit(
        self,
        schema_relation_id: str,
        is_directed: bool,
        mention_head_id: int,
        mention_tail_id: int,
        document_edit_id: int,
        document_recommendation_id=None,
        is_shown_recommendation=False,
    ) -> Relation:
        """
        Saves relation in the database.
        Does not check for valid inputs.

        :param schema_relation_id: SchemaRelation ID of relation
        :param is_directed: Is Relation directed
        :param mention_head_id: MentionHead ID of relation
        :param mention_tail_id: MentionTail ID of relation
        :param document_edit_id: Document edit ID of relation
        :param document_recommendation_id: Document recommendation ID of relation
        :param is_shown_recommendation: is relation a shown recommendation
        :return: Newly created Relation
        """
        return self.__relation_repository.save_relation_in_edit(
            schema_relation_id,
            is_directed,
            mention_head_id,
            mention_tail_id,
            document_edit_id,
            document_recommendation_id,
            is_shown_recommendation,
        )

    def delete_relation_by_id(self, relation_id):
        self.relation_mention_service.delete_relation_by_id(relation_id)

    def create_relation(
        self,
        schema_relation_id,
        document_edit_id,
        mention_head_id,
        mention_tail_id,
    ):
        self.mention_service.verify_mention_in_document_edit_not_recommendation(
            mention_head_id, document_edit_id
        )
        self.mention_service.verify_mention_in_document_edit_not_recommendation(
            mention_tail_id, document_edit_id
        )

        self.mention_service.check_mentions_not_equal(mention_head_id, mention_tail_id)

        self.__check_duplicate_relations(mention_head_id, mention_tail_id)

        # Check constraints for relation creation
        schema = self.schema_service.get_schema_by_document_edit(document_edit_id)
        schema_extended = self.schema_service.get_schema_by_id(schema.id)
        constraint = self.schema_service.verify_constraint(
            schema_extended,
            schema_relation_id,
            self.mention_service.get_mention_by_id(mention_head_id).schema_mention_id,
            self.mention_service.get_mention_by_id(mention_tail_id).schema_mention_id,
        )

        # save relation
        relation = self.__relation_repository.create_relation(
            schema_relation_id,
            document_edit_id,
            constraint["is_directed"],
            mention_head_id,
            mention_tail_id,
        )
        return self.get_relation_dto_by_id(relation.id)

    def update_relation(
        self,
        relation_id,
        schema_relation_id=None,
        mention_head_id=None,
        mention_tail_id=None,
    ):
        """
        Updates a relation with specified parameters.

        :param relation_id: Mention ID to update.
        :param schema_relation_id: Updated schema mention ID.
        :param mention_head_id: Updated MentionHead ID.
        :param mention_tail_id: Updated MentionTail ID.
        :return: relation_output_model
        :raises NotFound: If relation or mentions do not exist.
        :raises Conflict: If mentions already part of another relation.
        :raises BadRequest: If schema constraint is violated or relation is a recommendation.
        """
        relation = self.__relation_repository.get_relation_by_id(relation_id)
        if not relation:
            raise NotFound("Relation not found.")

        if relation.document_recommendation_id is not None:
            raise BadRequest("You cannot update a recommendation")

        if mention_head_id:
            # Verify mention
            mention_head = (
                self.mention_service.verify_mention_in_document_edit_not_recommendation(
                    mention_head_id, relation.document_edit_id
                )
            )
        else:
            mention_head = self.mention_service.get_mention_by_id(
                relation.mention_head_id
            )

        if mention_tail_id:
            mention_tail = (
                self.mention_service.verify_mention_in_document_edit_not_recommendation(
                    mention_tail_id, relation.document_edit_id
                )
            )
        else:
            mention_tail = self.mention_service.get_mention_by_id(
                relation.mention_tail_id
            )

        self.mention_service.check_mentions_not_equal(mention_head.id, mention_tail.id)

        # check duplicate relation if mentions changed
        if mention_tail_id or mention_head_id:
            duplicate_relations = (
                self.__relation_repository.get_relations_by_mention_head_and_tail(
                    mention_head.id, mention_tail.id
                )
            )
            if duplicate_relations is not None and len(duplicate_relations) > 0:
                # when no mention of relation changed, no conflict shall be returned
                if (
                    len(duplicate_relations) > 1
                    or duplicate_relations[0].id != relation.id
                ):
                    raise Conflict("Relation already exists.")

        # Check constraints for relation creation
        if schema_relation_id is not None:
            schema_relation = self.schema_service.get_schema_relation_by_id(
                schema_relation_id
            )
        else:
            schema_relation = self.schema_service.get_schema_relation_by_id(
                relation.schema_relation_id
            )

        schema = self.schema_service.get_schema_by_document_edit(
            relation.document_edit_id
        )
        schema_extended = self.schema_service.get_schema_by_id(schema.id)
        constraint = self.schema_service.verify_constraint(
            schema_extended,
            schema_relation.id,
            mention_head.schema_mention_id,
            mention_tail.schema_mention_id,
        )

        # update relation
        relation = self.__relation_repository.update_relation(
            relation_id,
            schema_relation_id,
            mention_head_id,
            mention_tail_id,
            constraint["is_directed"],
        )
        return self.get_relation_dto_by_id(relation.id)

    def get_relation_dto_by_id(self, relation_id):
        """
        Fetches relation and maps it to output dto.
        Also fetches associated mentions.

        :param relation_id: Relation ID to fetch
        :return: relation_output_model
        """
        relation = self.__relation_repository.get_relation_with_schema_by_id(
            relation_id
        )
        response = {
            "id": relation.relation_id,
            "tag": relation.tag,
            "isShownRecommendation": relation.isShownRecommendation,
            "isDirected": relation.isDirected,
            "document_edit_id": relation.document_edit_id,
            "document_recommendation_id": relation.document_recommendation_id,
            "head_mention": self.mention_service.get_mention_dto_by_id(
                relation.mention_head_id
            ),
            "tail_mention": self.mention_service.get_mention_dto_by_id(
                relation.mention_tail_id
            ),
            "schema_relation": {
                "id": relation.schema_relation_id,
                "tag": relation.tag,
                "description": relation.description,
                "schema_id": relation.schema_id,
            },
        }
        return response

    def accept_relation(self, relation_id):
        """
        Accept a relation by copying it to the document edit and setting isShownRecommendation to False.
        """
        relation = self.__relation_repository.get_relation_by_id(relation_id)

        if not relation or relation.document_recommendation_id is None:
            raise BadRequest("Invalid relation.")
        if not relation.isShownRecommendation:
            raise BadRequest("Relation recommendation already processed.")

        # Create new relation
        new_relation = self.__relation_repository.create_relation(
            schema_relation_id=relation.schema_relation_id,
            document_edit_id=relation.document_edit_id,
            isDirected=relation.isDirected,
            mention_head_id=relation.mention_head_id,
            mention_tail_id=relation.mention_tail_id,
            document_recommendation_id=None,
            is_shown_recommendation=False,
        )

        # Update relation recommendation
        self.__relation_repository.update_is_shown_recommendation(relation_id, False)
        return self.get_relation_dto_by_id(new_relation.id)

    def reject_relation(self, relation_id):
        """
        Reject a relation by setting isShownRecommendation to False.
        """
        relation = self.__relation_repository.get_relation_by_id(relation_id)

        if not relation or relation.document_recommendation_id is None:
            raise BadRequest("Invalid relation.")
        if not relation.isShownRecommendation:
            raise BadRequest("Relation recommendation already processed.")

        # Update relation recommendation
        self.__relation_repository.update_is_shown_recommendation(relation_id, False)
        return {"message": "Relation successfully rejected."}

    def __check_duplicate_relations(self, mention_head_id, mention_tail_id):
        """
        Checks if relation containing with the same mentions already exists.
        :param mention_head_id: MentionHead ID to check
        :param mention_tail_id: MentionTail ID to check
        :raises Conflict: If relation already exists
        """
        # get duplicate relation if any
        duplicate_relations = (
            self.__relation_repository.get_relations_by_mention_head_and_tail(
                mention_head_id, mention_tail_id
            )
        )

        # check for duplicate mention
        if duplicate_relations is not None:
            if len(duplicate_relations) > 0:
                raise Conflict("Relation already exists.")

    def get_recommendations_by_document_edit(self, document_edit_id):
        """
        Fetches all unreviewed relation recommendations for a document edit

        :param document_edit_id: Document Edit ID to query
        :return: List of relation database entries
        """
        return self.__relation_repository.get_recommendations_by_document_edit(
            document_edit_id
        )


relation_service = RelationService(
    RelationRepository(),
    user_service,
    schema_service,
    mention_service,
    relation_mention_service,
)
