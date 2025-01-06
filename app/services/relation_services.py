from werkzeug.exceptions import BadRequest, NotFound, Conflict

from app.repositories.mention_repository import MentionRepository
from app.repositories.relation_repository import RelationRepository
from app.services.user_service import UserService, user_service


class RelationService:
    def __init__(self, relation_repository, mention_repository):
        self.__relation_repository = relation_repository
        self.__mention_repository = mention_repository

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
            {
                "id": relation.id,
                "tag": relation.tag,
                "isShownRecommendation": relation.isShownRecommendation,
                "isDirected": relation.isDirected,
                "mention_head_id": relation.mention_head_id,
                "mention_tail_id": relation.mention_tail_id,
            }
            for relation in relations
        ]

        return {"relations": relation_list}

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
        logged_in_user_id = user_service.get_logged_in_user_id()
        document_edit_user_id = user_service.get_user_by_document_edit_id(
            data["document_edit_id"]
        )

        if logged_in_user_id != document_edit_user_id:
            raise NotFound("The logged in user does not belong to this document.")

        # get mention head and tail
        mention_head = self.__mention_repository.get_mention_by_id(
            data["mention_head_id"]
        )
        mention_tail = self.__mention_repository.get_mention_by_id(
            data["mention_tail_id"]
        )

        # check for none
        if mention_head is None or mention_tail is None:
            raise BadRequest("Invalid mention ids.")

        # get duplicate relation if any
        duplicate_relations = (
            self.__relation_repository.get_relations_by_mention_head_and_tail(
                mention_head.id, mention_tail.id
            )
        )

        # check for duplicate mention
        if duplicate_relations is not None:
            if len(duplicate_relations) > 0:
                raise Conflict("Token mention already exists.")

        # save relation
        relation = self.__relation_repository.create_relation(
            data["tag"],
            data["document_edit_id"],
            data["isDirected"],
            mention_head.id,
            mention_tail.id,
        )

        response = {
            "id": relation.id,
            "tag": relation.tag,
            "isShownRecommendation": relation.isShownRecommendation,
            "isDirected": relation.isDirected,
            "mention_head_id": relation.mention_head_id,
            "mention_tail_id": relation.mention_tail_id,
        }

        return response


relation_service = RelationService(RelationRepository(), MentionRepository())
