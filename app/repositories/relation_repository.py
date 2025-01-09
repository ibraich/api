from app.models import Mention,Relation
from app.db import db
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session 


class RelationRepository(BaseRepository):
    def __init__(self):
        self.db_session = db.session  # Automatically use the global db.session

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
    def set_is_shown_recommendation_false(self, relation_id):
        relation = self.db_session.query(Relation).filter_by(id=relation_id).first()
        if relation:
            relation.is_shown_recommendation = False
            self.db_session.commit()
        return relation

    def copy_to_document_edit(self, relation, user_id):
        new_relation = Relation(
            source=relation.source,
            target=relation.target,
            tag=relation.tag,
            document_edit_id=relation.document_edit_id,
            user_id=user_id,
            is_shown_recommendation=False,
            document_recommendation_id=None,
        )
        self.db_session.add(new_relation)
        self.db_session.commit()
        return new_relation
    


    def update_is_shown_recommendation(session, relation_id, is_shown: bool):
        relation = session.query(Relation).filter(Relation.id == relation_id).one_or_none()
        if relation:
            relation.is_shown_recommendation = is_shown
            session.commit()
            return relation
        return None

    def create_relation_in_edit(session, relation_data):
        new_relation = Relation(**relation_data)
        session.add(new_relation)
        session.commit()
        return new_relation
