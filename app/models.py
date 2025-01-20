import typing

from sqlalchemy import text

from app.db import db


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


class Team(db.Model):
    __tablename__ = "Team"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=text("true")
    )


class UserTeam(db.Model):
    __tablename__ = "UserTeam"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("Team.id"), nullable=False)


class Schema(db.Model):
    __tablename__ = "Schema"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=False, nullable=False)
    isFixed = db.Column(db.Boolean, nullable=False, default=False)
    modellingLanguage_id = db.Column(
        db.Integer, db.ForeignKey("ModellingLanguage.id"), nullable=False
    )
    team_id = db.Column(db.Integer, db.ForeignKey("Team.id"), nullable=False)
    active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=text("true")
    )

    # References
    modelling_language = db.relationship(
        "ModellingLanguage", foreign_keys=[modellingLanguage_id]
    )
    team = db.relationship(Team, foreign_keys=[team_id])

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "id": self.id,
            "name": self.name,
            "isFixed": self.isFixed,
            "modelling_language": (
                self.modelling_language.to_dict() if self.modelling_language else None
            ),
            "team": self.team.to_dict() if self.team else None,
        }


class SchemaMention(db.Model):
    __tablename__ = "SchemaMention"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    tag = db.Column(db.String, nullable=False)
    entityPossible = db.Column(db.Boolean, nullable=False, default=True)
    color = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "id": self.id,
            "schema_id": self.schema_id,
            "tag": self.tag,
            "entityPossible": self.entityPossible,
            "color": self.color,
            "description": self.description,
        }


class SchemaRelation(db.Model):
    __tablename__ = "SchemaRelation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    tag = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "id": self.id,
            "schema_id": self.schema_id,
            "tag": self.tag,
            "description": self.description,
        }


class SchemaConstraint(db.Model):
    __tablename__ = "SchemaConstraint"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_relation_id = db.Column(
        db.Integer, db.ForeignKey("SchemaRelation.id"), nullable=False
    )
    schema_mention_id_head = db.Column(db.Integer, nullable=False)
    schema_mention_id_tail = db.Column(db.Integer, nullable=False)
    isDirected = db.Column(db.Boolean, nullable=False, default=True)


class Project(db.Model):
    __tablename__ = "Project"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("Team.id"), nullable=False)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=text("true")
    )

    # Creator can always be added when querying project
    creator = db.relationship("User", foreign_keys="Project.creator_id")

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "id": self.id,
            "name": self.name,
            "creator": (
                self.creator.to_dict() if self.creator else {"id": self.creator_id}
            ),
        }


class DocumentRecommendation(db.Model):
    __tablename__ = "DocumentRecommendation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documentEditHash = db.Column(db.String(), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("Document.id"), nullable=True)
    document_edit_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEdit.id"), nullable=True
    )
    state_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEditState.id"), nullable=False
    )


class Token(db.Model):
    __tablename__ = "Token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(), nullable=False)
    document_index = db.Column(db.Integer, nullable=False)
    sentence_index = db.Column(db.Integer, nullable=False)
    pos_tag = db.Column(db.String(), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey("Document.id"), nullable=False)

    # Relationships
    token_mentions = db.relationship("TokenMention", back_populates="token", lazy=True)

    def __repr__(self):
        return f"Token(id={self.id}, text={self.text}, document_index={self.document_index}, sentence_index={self.sentence_index}, pos_tag={self.pos_tag}, document_id={self.document_id})"

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "id": self.id,
            "text": self.text,
            "document_index": self.document_index,
            "sentence_index": self.sentence_index,
            "pos_tag": self.pos_tag,
        }


class Mention(db.Model):
    __tablename__ = "Mention"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_mention_id = db.Column(
        db.Integer, db.ForeignKey("SchemaMention.id"), nullable=False
    )
    isShownRecommendation = db.Column(db.Boolean, nullable=False, default=False)
    document_edit_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEdit.id"), nullable=True
    )
    document_recommendation_id = db.Column(
        db.Integer, db.ForeignKey("DocumentRecommendation.id"), nullable=True
    )
    entity_id = db.Column(db.Integer, db.ForeignKey("Entity.id"), nullable=True)

    # Relationships
    token_mentions = db.relationship(
        "TokenMention", back_populates="mention", lazy=True
    )
    entity = db.relationship("Entity", back_populates="mentions")
    schema_mention = db.relationship("SchemaMention", foreign_keys=[schema_mention_id])

    def __repr__(self):
        return f"Mention(id={self.id}, tag={self.tag}, isShownRecommendation={self.isShownRecommendation}, entity={self.entity.__repr__()}, tokens={[tm.token.__repr__() for tm in self.token_mentions]}, document_edit_id={self.document_edit_id}, document_recommendation_id={self.document_recommendation_id})"

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        mention_dto = {
            "id": self.id,
            "tokens": [tm.token.to_dict() for tm in self.token_mentions],
            "entity": self.entity.to_dict(),
        }
        if self.schema_mention:
            mention_dto["schema_mention"] = self.schema_mention.to_dict()
            mention_dto["tag"] = (
                self.schema_mention.tag  # denormalized for pipeline input
            )
        else:
            mention_dto["schema_mention"] = {"id": self.schema_mention_id}
        return mention_dto


class TokenMention(db.Model):
    __tablename__ = "TokenMention"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token_id = db.Column(db.Integer, db.ForeignKey("Token.id"), nullable=False)
    mention_id = db.Column(db.Integer, db.ForeignKey("Mention.id"), nullable=False)

    # Relationships
    token = db.relationship("Token", back_populates="token_mentions")
    mention = db.relationship("Mention", back_populates="token_mentions")


class Entity(db.Model):
    __tablename__ = "Entity"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isShownRecommendation = db.Column(db.Boolean, nullable=False, default=False)
    document_edit_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEdit.id"), nullable=True
    )
    document_recommendation_id = db.Column(
        db.Integer, db.ForeignKey("DocumentRecommendation.id"), nullable=True
    )

    # Relationships
    mentions = db.relationship("Mention", back_populates="entity")

    def __repr__(self):
        return (
            f"Entity(id={self.id}, isShownRecommendation={self.isShownRecommendation})"
        )

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "id": self.id,
            "isShownRecommendation": self.isShownRecommendation,
        }


class Relation(db.Model):
    __tablename__ = "Relation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isShownRecommendation = db.Column(db.Boolean, nullable=False, default=False)
    schema_relation_id = db.Column(
        db.Integer, db.ForeignKey("SchemaRelation.id"), nullable=False
    )
    isDirected = db.Column(db.Boolean, nullable=False, default=True)
    mention_head_id = db.Column(db.Integer, db.ForeignKey("Mention.id"), nullable=False)
    mention_tail_id = db.Column(db.Integer, db.ForeignKey("Mention.id"), nullable=False)
    document_edit_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEdit.id"), nullable=True
    )
    document_recommendation_id = db.Column(
        db.Integer, db.ForeignKey("DocumentRecommendation.id"), nullable=True
    )

    # Relationships
    mention_head = db.relationship(
        "Mention", foreign_keys=[mention_head_id], backref="relations_as_head"
    )
    mention_tail = db.relationship(
        "Mention", foreign_keys=[mention_tail_id], backref="relations_as_tail"
    )
    schema_relation = db.relationship(
        "SchemaRelation", foreign_keys=[schema_relation_id]  # , backref="relations"
    )

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        relation_dto = {
            "id": self.id,
            "isShownRecommendation": self.isShownRecommendation,
            "isDirected": self.isDirected,
            "mention_head": self.mention_head.to_dict() if self.mention_head else None,
            "mention_tail": self.mention_tail.to_dict() if self.mention_tail else None,
            "document_edit_id": self.document_edit_id,
            "document_recommendation_id": self.document_recommendation_id,
        }
        if self.schema_relation:
            relation_dto["schema_relation"] = self.schema_relation.to_dict()
            relation_dto["tag"] = (
                self.schema_relation.tag  # denormalized for pipeline input
            )
        else:
            relation_dto["schema_relation"] = {"id": self.schema_relation_id}
        return relation_dto


class DocumentEdit(db.Model):
    __tablename__ = "DocumentEdit"
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_id = db.Column(
        db.Integer, db.ForeignKey("DocumentEditState.id"), nullable=False
    )
    document_id = db.Column(db.Integer, db.ForeignKey("Document.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=text("true")
    )

    # Relationships
    document = db.relationship(
        "Document", back_populates="document_edits", lazy="select"
    )

    # user & state can always be added when querying DocumentEdit
    user = db.relationship("User", foreign_keys="DocumentEdit.user_id")
    state = db.relationship("DocumentEditState", foreign_keys="DocumentEdit.state_id")

    # Add lists if required to improve performance
    mentions: typing.List[Mention]
    relations: typing.List[Relation]

    def __repr__(self):
        return f"DocumentEdit(id={self.id}, state_id={self.state_id}, document={self.document}, mentions={[m.id for m in self.mentions]}, relations={[r.id for r in self.relations]})"

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        document_edit = {
            "document": self.document.to_dict(),
            "user": self.user.to_dict() if self.user else {"id": self.user_id},
            "state": self.state.to_dict() if self.state else {"id": self.state_id},
        }
        if self.mentions:
            document_edit["mentions"] = [mention.to_dict() for mention in self.mentions]
        if self.relations:
            document_edit["relations"] = [
                relation.to_dict() for relation in self.relations
            ]
        return document_edit


class ModellingLanguage(db.Model):
    __tablename__ = "ModellingLanguage"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)


class DocumentState(db.Model):
    __tablename__ = "DocumentState"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
        }


class Document(db.Model):
    __tablename__ = "Document"
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=False, nullable=False)
    content = db.Column(db.String(), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey("DocumentState.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("Project.id"), nullable=False)
    active = db.Column(
        db.Boolean, nullable=False, default=True, server_default=text("true")
    )

    # Relationships
    document_edits = db.relationship(
        "DocumentEdit", back_populates="document", lazy="select"
    )

    # Creator, state & project can always be added when querying Document
    creator = db.relationship("User", foreign_keys="Document.creator_id")
    state = db.relationship("DocumentState", foreign_keys="Document.state_id")
    project = db.relationship("Project", foreign_keys="Document.project_id")

    # Add lists if required to improve performance
    tokens: typing.List["Token"]

    def __repr__(self):
        return f"Document(id={self.id}, name={self.name}, content={self.content}, creator={self.creator.__repr__()}, tokens={[t.id for t in self.tokens] if self.tokens else None}, document_edits={[de.id for de in self.document_edits]})"

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "tokens": [token.to_dict() for token in self.tokens],
            "creator": (
                self.creator.to_dict() if self.creator else {"id": self.creator_id}
            ),
            "state": self.state.to_dict() if self.state else {"id": self.state_id},
            "project": (
                self.project.to_dict() if self.project else {"id": self.project_id}
            ),
        }


class DocumentEditState(db.Model):
    __tablename__ = "DocumentEditState"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
        }


def insert_default_values(types, model):
    for t in types:
        if db.session.query(model.id).filter_by(type=t).first() is None:
            db.session.add(model(type=t))
            db.session.commit()
