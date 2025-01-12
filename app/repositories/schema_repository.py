from sqlalchemy.orm import aliased

from app.models import (
    Schema,
    Team,
    ModellingLanguage,
    SchemaMention,
    SchemaRelation,
    SchemaConstraint,
    UserTeam,
    Project,
)
from app.repositories.base_repository import BaseRepository
from app.db import db, Session

ModellingLanguagesByName = {
    "BPMN": 1,
}


class SchemaRepository(BaseRepository):
    def get_schema_by_id(self, schema_id):
        return (
            Session.query(
                Schema.id,
                Schema.isFixed,
                Schema.team_id,
                Schema.name,
                Team.name.label("team_name"),
                ModellingLanguage.type.label("modelling_language"),
            )
            .join(Team, Schema.team_id == Team.id)
            .join(
                ModellingLanguage, ModellingLanguage.id == Schema.modellingLanguage_id
            )
            .filter((Schema.id == schema_id) & (Schema.active == True))
            .first()
        )

    def get_schema_ids_by_user(self, user_id):
        return (
            db.session.query(Schema.id)
            .select_from(UserTeam)
            .join(Schema, Schema.team_id == UserTeam.team_id)
            .filter((UserTeam.user_id == user_id) & (Schema.active == True))
            .all()
        )

    def get_schema_mentions_by_schema(self, schema_id):
        return (
            Session.query(SchemaMention)
            .filter(SchemaMention.schema_id == schema_id)
            .all()
        )

    def get_schema_relations_by_schema(self, schema_id):
        return (
            Session.query(SchemaRelation)
            .filter(SchemaRelation.schema_id == schema_id)
            .all()
        )

    def get_by_project(self, project_id):
        return (
            db.session.query(
                Schema.id,
                Schema.isFixed,
                Schema.team_id,
                Schema.name,
                Team.name.label("team_name"),
                ModellingLanguage.type.label("modelling_language"),
            )
            .join(Team, Schema.team_id == Team.id)
            .join(
                ModellingLanguage, ModellingLanguage.id == Schema.modellingLanguage_id
            )
            .join(Project, Project.schema_id == Schema.id)
            .filter(Project.id == project_id)
            .first()
        )

    def get_schema_constraints_by_schema(self, schema_id):
        mention_head = aliased(SchemaMention)
        mention_tail = aliased(SchemaMention)
        return (
            Session.query(
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

    def create_schema(
        self, modelling_language_id: int, team_id: int, name: str
    ) -> Schema:
        return super().store_object_transactional(
            Schema(
                modellingLanguage_id=modelling_language_id,
                team_id=team_id,
                active=True,
                name=name,
            )
        )

    def create_schema_mention(
        self,
        schema_id: int,
        tag: str,
        description: str,
        entity_possible: bool,
        color: str,
    ) -> SchemaMention:
        return super().store_object_transactional(
            SchemaMention(
                schema_id=schema_id,
                tag=tag,
                description=description,
                entityPossible=entity_possible,
                color=color,
            )
        )

    def create_schema_relation(
        self, schema_id: int, tag: str, description: str
    ) -> SchemaRelation:
        return super().store_object_transactional(
            SchemaRelation(schema_id=schema_id, tag=tag, description=description)
        )

    def create_schema_constraint(
        self,
        schema_relation_id: int,
        schema_mention_id_head: int,
        schema_mention_id_tail: int,
        is_directed: bool,
    ) -> SchemaConstraint:
        return super().store_object_transactional(
            SchemaConstraint(
                schema_relation_id=schema_relation_id,
                schema_mention_id_head=schema_mention_id_head,
                schema_mention_id_tail=schema_mention_id_tail,
                isDirected=is_directed,
            )
        )
