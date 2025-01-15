from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.repositories.mention_repository import MentionRepository
from app.models import Relation
from app.repositories.relation_repository import RelationRepository
from app.services.user_service import user_service


class RelationService:
    def __init__(self, relation_repository, mention_repository, user_service):
        self.__relation_repository = relation_repository
        self.__mention_repository = mention_repository
        self.user_service = user_service
        self.relation_repository = relation_repository

    def get_relations_by_document_edit(self, document_edit_id):
        if not isinstance(document_edit_id, int) or document_edit_id <= 0:
            raise BadRequest("Invalid document edit ID. It must be a positive integer.")

        relations = self.__relation_repository.get_relations_by_document_edit(
            document_edit_id
        )

        if not relations:
            raise NotFound("No relations found for the given document edit.")

        # Serialize mentions to JSON-compatible format
        relation_list = [
            self.map_to_relation_output_dto(relation) for relation in relations
        ]

        return {"relations": relation_list}

    def save_relation_in_edit(
        self,
        tag: str,
        is_directed: bool,
        mention_head_id: int,
        mention_tail_id: int,
        document_edit_id: int,
    ) -> Relation:
        return self.__relation_repository.save_relation_in_edit(
            tag, is_directed, mention_head_id, mention_tail_id, document_edit_id
        )

    def delete_relation_by_id(self, relation_id):
        if not isinstance(relation_id, int) or relation_id <= 0:
            raise BadRequest("Invalid relation ID. It must be a positive integer.")

        # Fetch the relation to perform validation
        relation = self.__relation_repository.get_relation_by_id(relation_id)
        if not relation:
            raise NotFound("Relation not found.")

        # Check if document_edit_id is null
        if relation.document_edit_id is None:
            raise BadRequest(
                "Cannot delete a relation without a valid document_edit_id."
            )

        # logged_in_user_id = user_service.get_logged_in_user_id()
        # document_edit_user_id = user_service.get_user_by_document_edit_id(relation.document_edit_id)

        # if logged_in_user_id != document_edit_user_id:
        # raise NotFound("The logged in user does not belong to this document.")

        # Proceed with deletion
        deleted = self.__relation_repository.delete_relation_by_id(relation_id)
        if not deleted:
            raise NotFound("Relation not found during deletion.")

        return {"message": "OK"}

    def get_relations_by_mention(self, mention_id):
        return self.__relation_repository.get_relations_by_mention(mention_id)

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

        # save relation
        relation = self.__relation_repository.create_relation(
            data["tag"],
            data["document_edit_id"],
            data["isDirected"],
            data["mention_head_id"],
            data["mention_tail_id"],
        )

        return self.map_to_relation_output_dto(relation)

    def update_relation(
        self, relation_id, tag, mention_head_id, mention_tail_id, is_directed
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
            self.verify_mention_in_document_edit(
                mention_head_id, relation.document_edit_id
            )
        if mention_tail_id:
            self.verify_mention_in_document_edit(
                mention_tail_id, relation.document_edit_id
            )

        updated_mention_head_id = (
            mention_head_id if mention_head_id is not None else relation.mention_head_id
        )
        updated_mention_tail_id = (
            mention_tail_id if mention_tail_id is not None else relation.mention_tail_id
        )

        self.check_mentions_not_equal(updated_mention_head_id, updated_mention_tail_id)

        # check duplicate relation if mentions changed
        if mention_tail_id or mention_head_id:
            duplicate_relations = (
                self.__relation_repository.get_relations_by_mention_head_and_tail(
                    updated_mention_head_id, updated_mention_tail_id
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

        # update relation
        relation = self.__relation_repository.update_relation(
            relation_id, tag, mention_head_id, mention_tail_id, is_directed
        )

        return self.map_to_relation_output_dto(relation)

    def map_to_relation_output_dto(self, relation):
        response = {
            "id": relation.id,
            "tag": relation.tag,
            "isShownRecommendation": relation.isShownRecommendation,
            "isDirected": relation.isDirected,
            "mention_head_id": relation.mention_head_id,
            "mention_tail_id": relation.mention_tail_id,
        }
        return response
    


    def accept_relation(self, relation_id, document_edit_id):
        """
        Akzeptiert eine Relation, indem sie kopiert und isShownRecommendation auf False gesetzt wird.
        """
        relation = self.relation_repository.get_relation_by_id(relation_id)
        if not relation or relation.document_edit_id != document_edit_id:
            raise ValueError("Invalid relation or unauthorized access.")
        if not relation.isShownRecommendation:
            raise ValueError("Relation recommendation already processed.")
            # Neue Relation erstellen
        new_relation = self.relation_repository.create_relation(
            tag=relation.tag,
            document_edit_id=document_edit_id,
            is_directed=relation.isDirected,
            mention_head_id=relation.mention_head_id,
            mention_tail_id=relation.mention_tail_id,
            document_recommendation_id=None,
            is_shown_recommendation=False,
        )
        # Original Relation aktualisieren
        self.relation_repository.update_is_shown_recommendation(relation_id, False)
        return new_relation
    def reject_relation(self, relation_id, document_edit_id):
        """
        Lehnt eine Relation ab, indem isShownRecommendation auf False gesetzt wird.
        """
        relation = self.relation_repository.get_relation_by_id(relation_id)
        if not relation or relation.document_edit_id != document_edit_id:
            raise ValueError("Invalid relation or unauthorized access.")
        if not relation.isShownRecommendation:
            raise ValueError("Relation recommendation already processed.")
        # Original Relation aktualisieren
        return self.relation_repository.update_is_shown_recommendation(relation_id, False)


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
        mention = self.__mention_repository.get_mention_by_id(mention_id)

        # check for none and if mention belongs to same edit
        if mention is None or mention.document_edit_id != document_edit_id:
            raise BadRequest("Invalid mention ids.")

        if mention.document_recommendation_id:
            raise BadRequest("You cannot use a recommendation inside the relation")

    def check_mentions_not_equal(self, mention_head_id, mention_tail_id):
        if mention_head_id == mention_tail_id:
            raise BadRequest("Mentions are equal")


relation_service = RelationService(
    RelationRepository(), MentionRepository(), user_service
)
