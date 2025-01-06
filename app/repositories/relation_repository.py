from app.models import Relation
from app.db import db
from app.repositories.base_repository import BaseRepository


class RelationRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

    def create_relation(
        self,
        tag,
        document_edit_id,
        isDirected,
        mention_head_id,
        mention_tail_id,
        document_recommendation_id=None,
        is_shown_recommendation=False,
    ):

        relation = Relation(
            tag=tag,
            document_edit_id=document_edit_id,
            isDirected=isDirected,
            mention_head_id=mention_head_id,
            mention_tail_id=mention_tail_id,
            document_recommendation_id=document_recommendation_id,
            isShownRecommendation=is_shown_recommendation,
        )
        self.store_object(relation)
        return relation

    def get_relations_by_document_edit(self, document_edit_id):
        return (
            self.db_session.query(Relation)
            .filter(
                (Relation.document_edit_id == document_edit_id)
                & (
                    Relation.document_recommendation_id.is_(None)
                    | Relation.isShownRecommendation.is_(True)
                )
            )
            .all()
        )

    def delete_relation_by_id(self, relation_id):
        relation = self.db_session.query(Relation).filter_by(id=relation_id).first()
        if not relation:
            return False
        self.db_session.delete(relation)
        self.db_session.commit()
        return True

    def get_relation_by_id(self, relation_id):
        return self.db_session.query(Relation).filter_by(id=relation_id).first()

    def get_relations_by_mention(self, mention_id):
        return (
            self.db_session.query(Relation)
            .filter(
                (Relation.mention_head_id == mention_id)
                | (Relation.mention_tail_id == mention_id)
            )
            .all()
        )

    def get_relations_by_mention_head_and_tail(self, mention_head_id, mention_tail_id):
        return (
            self.db_session.query(Relation)
            .filter(
                (
                    (Relation.mention_head_id == mention_head_id)
                    & (Relation.mention_tail_id == mention_tail_id)
                )
                | (
                    (Relation.mention_head_id == mention_tail_id)
                    & (Relation.mention_tail_id == mention_head_id)
                    & (Relation.isDirected == False)
                )
            )
            .all()
        )

    def delete_relations_by_mention(self, mention_id):
        relations = self.get_relations_by_mention(mention_id)
        for relation in relations:
            self.db_session.delete(relation)
        self.db_session.commit()
