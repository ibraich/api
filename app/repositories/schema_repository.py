from sqlalchemy.orm import aliased

from app.models import (
    Schema,
    Team,
    ModellingLanguage,
    SchemaMention,
    SchemaRelation,
    SchemaConstraint,
    UserTeam,
)
from app.repositories.base_repository import BaseRepository
from app.db import db


class SchemaRepository(BaseRepository):
    def get_schema_by_id(self, schema_id):
        return (
            db.session.query(
                Schema.id,
                Schema.isFixed,
                Schema.team_id,
                Team.name.label("team_name"),
                ModellingLanguage.type.label("modelling_language"),
            )
            .join(Team, Schema.team_id == Team.id)
            .join(
                ModellingLanguage, ModellingLanguage.id == Schema.modellingLanguage_id
            )
            .filter(Schema.id == schema_id)
            .first()
        )

    def get_schema_ids_by_user(self, user_id):
        return (
            db.session.query(Schema.id)
            .select_from(UserTeam)
            .filter(UserTeam.user_id == user_id)
            .join(Schema, Schema.team_id == UserTeam.team_id)
            .all()
        )

    def get_schema_mentions_by_schema(self, schema_id):
        return (
            db.session.query(SchemaMention)
            .filter(SchemaMention.schema_id == schema_id)
            .all()
        )

    def get_schema_relations_by_schema(self, schema_id):
        return (
            db.session.query(SchemaRelation)
            .filter(SchemaRelation.schema_id == schema_id)
            .all()
        )

    def get_schema_constraints_by_schema(self, schema_id):
        mention_head = aliased(SchemaMention)
        mention_tail = aliased(SchemaMention)
        return (
            db.session.query(
                SchemaConstraint.id,
                SchemaConstraint.isDirected,
                SchemaRelation.id.label("relation_id"),
                SchemaRelation.tag.label("relation_tag"),
                SchemaRelation.description.label("relation_description"),
                mention_head.id.label("mention_head_id"),
                mention_tail.id.label("mention_tail_id"),
                mention_head.tag.label("mention_head_tag"),
                mention_tail.tag.label("mention_tail_tag"),
                mention_head.description.label("mention_head_description"),
                mention_tail.description.label("mention_tail_description"),
                mention_head.color.label("mention_head_color"),
                mention_tail.color.label("mention_tail_color"),
                mention_head.entityPossible.label("mention_head_entityPossible"),
                mention_tail.entityPossible.label("mention_tail_entityPossible"),
            )
            .join(
                mention_head,
                mention_head.id == SchemaConstraint.schema_mention_id_head,
            )
            .join(
                mention_tail,
                mention_tail.id == SchemaConstraint.schema_mention_id_tail,
            )
            .join(
                SchemaRelation, SchemaRelation.id == SchemaConstraint.schema_relation_id
            )
            .filter(
                (SchemaRelation.schema_id == schema_id)
                & (SchemaConstraint.schema_relation_id == SchemaRelation.id)
            )
            .all()
        )
