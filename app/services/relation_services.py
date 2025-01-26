from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.models import Relation
from app.repositories.relation_repository import RelationRepository
from app.services.relation_mention_service import relation_mention_service
from app.services.schema_service import schema_service
from app.services.user_service import user_service
from app.services.mention_services import mention_service


class RelationService:
    def __init__(
        self,
        relation_repository,
        user_service,
        schema_service,
        mention_service,
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

        user_id = user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(user_id, document_edit_id)

        mentions_data = self.mention_service.get_mentions_by_document_edit(
            document_edit_id
        )
        mentions_dict = {
            mention["id"]: {
                "tag": mention["tag"],
                "tokens": mention["tokens"],
                "entity": mention["entity_id"],
            }
            for mention in mentions_data["mentions"]
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
    ) -> Relation:
        return self.__relation_repository.save_relation_in_edit(
            schema_relation_id,
            is_directed,
            mention_head_id,
            mention_tail_id,
            document_edit_id,
        )

    def delete_relation_by_id(self, relation_id):
        self.relation_mention_service.delete_relation_by_id(relation_id)

    def create_relation(self, data):
        # check if user is allowed to access this document edit
        logged_in_user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(
            logged_in_user_id, data["document_edit_id"]
        )

        self.verify_mention_in_document_edit(
            data["mention_head_id"], data["document_edit_id"]
        )
        self.verify_mention_in_document_edit(
            data["mention_tail_id"], data["document_edit_id"]
        )

        self.check_mentions_not_equal(data["mention_head_id"], data["mention_tail_id"])

        self.check_duplicate_relations(data["mention_head_id"], data["mention_tail_id"])

        # Check constraints for relation creation
        schema = self.schema_service.get_schema_by_document_edit(
            data["document_edit_id"]
        )
        schema_extended = self.schema_service.get_schema_by_id(schema.id)
        self.schema_service.verify_constraint(
            schema_extended,
            data["schema_relation_id"],
            self.mention_service.get_mention_by_id(
                data["mention_head_id"]
            ).schema_mention_id,
            self.mention_service.get_mention_by_id(
                data["mention_tail_id"]
            ).schema_mention_id,
            data["isDirected"],
        )

        # save relation
        relation = self.__relation_repository.create_relation(
            data["schema_relation_id"],
            data["document_edit_id"],
            data["isDirected"],
            data["mention_head_id"],
            data["mention_tail_id"],
        )
        schema_relation = self.schema_service.get_schema_relation_by_id(
            data["schema_relation_id"]
        )
        relation.schema_relation = schema_relation
        return relation

    def update_relation(
        self,
        relation_id,
        schema_relation_id,
        mention_head_id,
        mention_tail_id,
        is_directed,
    ):
        relation = self.__relation_repository.get_relation_by_id(relation_id)
        if not relation:
            raise NotFound("Relation not found.")

        if relation.document_recommendation_id is not None:
            raise BadRequest("You cannot update a recommendation")

        logged_in_user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(
            logged_in_user_id, relation.document_edit_id
        )

        if mention_head_id:
            mention_head = self.verify_mention_in_document_edit(
                mention_head_id, relation.document_edit_id
            )
        else:
            mention_head = self.mention_service.get_mention_by_id(mention_head_id)

        if mention_tail_id:
            mention_tail = self.verify_mention_in_document_edit(
                mention_tail_id, relation.document_edit_id
            )
        else:
            mention_tail = self.mention_service.get_mention_by_id(mention_tail_id)

        self.check_mentions_not_equal(mention_head.id, mention_tail.id)

        # check duplicate relation if mentions changed
        if mention_tail_id or mention_head_id:
            duplicate_relations = (
                self.__relation_repository.get_relations_by_mention_head_and_tail(
                    mention_head.id, mention_tail.id
                )
            )
            if duplicate_relations is not None and len(duplicate_relations) > 0:
                # when only one mention of relation changed, current relation will be returned as duplicate
                # when both mentions changed, no duplicate shall be returned
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
        self.schema_service.verify_constraint(
            schema_extended,
            schema_relation.id,
            mention_head.schema_mention_id,
            mention_tail.schema_mention_id,
            is_directed if is_directed is not None else relation.isDirected,
        )

        # update relation
        relation = self.__relation_repository.update_relation(
            relation_id,
            schema_relation_id,
            mention_head_id,
            mention_tail_id,
            is_directed,
        )
        relation.schema_relation = schema_relation
        return relation

    def map_to_relation_output_dto(self, relation):
        response = {
            "id": relation.id,
            "tag": relation.tag,
            "isShownRecommendation": relation.isShownRecommendation,
            "isDirected": relation.isDirected,
            "mention_head_id": relation.mention_head_id,
            "mention_tail_id": relation.mention_tail_id,
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
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(
            user_id, relation.document_edit_id
        )

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
        return new_relation

    def reject_relation(self, relation_id):
        """
        Reject a relation by setting isShownRecommendation to False.
        """
        relation = self.__relation_repository.get_relation_by_id(relation_id)
        user_id = self.user_service.get_logged_in_user_id()
        self.user_service.check_user_document_edit_accessible(
            user_id, relation.document_edit_id
        )

        if not relation or relation.document_recommendation_id is None:
            raise BadRequest("Invalid relation.")
        if not relation.isShownRecommendation:
            raise BadRequest("Relation recommendation already processed.")

        # Update relation recommendation
        self.__relation_repository.update_is_shown_recommendation(relation_id, False)
        return {"message": "Relation successfully rejected."}

    def check_duplicate_relations(self, mention_head_id, mention_tail_id):
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

    def verify_mention_in_document_edit(self, mention_id, document_edit_id):
        # get mention head and tail
        mention = self.mention_service.get_mention_by_id(mention_id)

        # check for none and if mention belongs to same edit
        if mention is None or mention.document_edit_id != document_edit_id:
            raise BadRequest("Invalid mention ids.")

        if mention.document_recommendation_id:
            raise BadRequest("You cannot use a recommendation inside the relation")
        return mention

    def check_mentions_not_equal(self, mention_head_id, mention_tail_id):
        if mention_head_id == mention_tail_id:
            raise BadRequest("Mentions are equal")


relation_service = RelationService(
    RelationRepository(),
    user_service,
    schema_service,
    mention_service,
    relation_mention_service,
)
