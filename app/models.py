import typing

from sqlalchemy import text

from app.db import db


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


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


class SchemaMention(db.Model):
    __tablename__ = "SchemaMention"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    tag = db.Column(db.String, nullable=False)
    entityPossible = db.Column(db.Boolean, nullable=False, default=True)
    color = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)


class SchemaRelation(db.Model):
    __tablename__ = "SchemaRelation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schema_id = db.Column(db.Integer, db.ForeignKey("Schema.id"), nullable=False)
    tag = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)


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


class Document(db.Model):
    __tablename__ = "Document"
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
    tokens = db.relationship("Token", back_populates="document")
    document_edits = db.relationship("DocumentEdit", back_populates="document")

    def __repr__(self):
        return f"Document(id={self.id}, name={self.name}, content={self.content}, creator_id={self.creator_id}, tokens={self.tokens.__repr__()}, document_edits={[de.__repr__() for de in self.document_edits]})"

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


class DocumentEdit(db.Model):
    __tablename__ = "DocumentEdit"
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
    document = db.relationship("Document", back_populates="document_edits")
    mentions = db.relationship(
        "Mention",
        foreign_keys="Mention.document_edit_id",  # Explicit foreign key
        backref=db.backref(
            "document_edit", lazy=False
        ),  # Avoid bidirectional relationship
        lazy="select",  # Optimize for lazy loading
    )
    relations = db.relationship(
        "Relation",
        foreign_keys="Relation.document_edit_id",  # Explicit foreign key
        backref=db.backref(
            "document_edit", lazy=False
        ),  # Avoid bidirectional relationship
        lazy="select",  # Optimize for lazy loading
    )

    entities: typing.ClassVar[typing.List["Entity"]]

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "document": self.document.to_dict(),
            "mentions": [mention.to_dict() for mention in self.mentions],
            "relations": [relation.to_dict() for relation in self.relations],
        }


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
    document = db.relationship("Document", back_populates="tokens", lazy=True)

    def __repr__(self):
        return f"Token(id={self.id}, text={self.text}, document_index={self.document_index}, sentence_index={self.sentence_index}, pos_tag={self.pos_tag}, document={self.document.__repr__()})"

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
    tag = db.Column(db.String(), nullable=False)
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

    def __repr__(self):
        return f"Mention(id={self.id}, tag={self.tag}, isShownRecommendation={self.isShownRecommendation}, entity={self.entity.__repr__()}, tokens={[tm.token.__repr__() for tm in self.token_mentions]})"

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "id": self.id,
            "tag": self.tag,
            "tokens": [tm.token.to_dict() for tm in self.token_mentions],
            "entity": self.entity.to_dict(),
        }


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
    tag = db.Column(db.String(), nullable=False)
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

    def to_dict(self):
        """
        mapping from business model to DTO
        :return: DTO as dictionary
        """
        return {
            "id": self.id,
            "isShownRecommendation": self.isShownRecommendation,
            "tag": self.tag,
            "isDirected": self.isDirected,
            "mention_head": self.mention_head.to_dict() if self.mention_head else None,
            "mention_tail": self.mention_tail.to_dict() if self.mention_tail else None,
            "document_edit_id": self.document_edit_id,
            "document_recommendation_id": self.document_recommendation_id,
        }


class ModellingLanguage(db.Model):
    __tablename__ = "ModellingLanguage"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)


class DocumentState(db.Model):
    __tablename__ = "DocumentState"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)


class DocumentEditState(db.Model):
    __tablename__ = "DocumentEditState"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(), unique=True, nullable=False)


def insert_default_values(types, model):
    for t in types:
        if db.session.query(model.id).filter_by(type=t).first() is None:
            db.session.add(model(type=t))
            db.session.commit()
