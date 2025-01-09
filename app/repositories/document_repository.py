from app.models import (
    Document,
    DocumentState,
    Project,
    DocumentEditState,
    DocumentEdit,
    Mention,
    Relation,
    Team,
    User,
    UserTeam,
    DocumentRecommendation,
)
from app.repositories.base_repository import BaseRepository
from sqlalchemy import and_
from app.db import db, Session


class DocumentRepository(BaseRepository):
    DOCUMENT_STATE_ID_FINISHED = 3

    def get_documents_by_user(self, user_id):
        return (
            db.session.query(
                Document.id,
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Team.name.label("team_name"),
                Team.id.label("team_id"),
                DocumentEditState.type.label("document_edit_state"),
                DocumentEdit.id.label("document_edit_id"),
            )
            .select_from(User)
            .filter(User.id == user_id)
            .join(UserTeam, User.id == UserTeam.user_id)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Team.id == Project.team_id)
            .join(Document, Project.id == Document.project_id)
            .join(DocumentState, DocumentState.id == Document.state_id)
            .outerjoin(
                DocumentEdit,
                and_(
                    Document.id == DocumentEdit.document_id,
                    DocumentEdit.user_id == user_id,
                ),
            )
            .outerjoin(DocumentEditState, DocumentEditState.id == DocumentEdit.state_id)
        )

    def create_document(self, name, content, project_id, user_id):
        """
        Creates and stores a document in the database.

        Args:
            name (str): Name of the document.
            content (str): Content of the document.
            project_id (int): ID of the associated project.
            user_id (int): ID of the associated creator.

        Returns:
            Document: The created Document object.
        """
        document = Document(
            name=name,
            content=content,
            project_id=project_id,
            creator_id=user_id,
            state_id=1,
        )
        self.store_object(document)
        return document
      
    def get_document_by_id(self, document_id):
        return (
            Session.query(
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Project.team_id,
                DocumentRecommendation.id.label("document_recommendation_id"),
            )
            .select_from(Document)
            .filter(Document.id == document_id)
            .join(Project, Project.id == Document.project_id)
            .outerjoin(
                DocumentRecommendation,
                and_(
                    Document.id == DocumentRecommendation.document_id,
                    DocumentRecommendation.document_edit_id is None,
                ),
            )
        ).first()

    def save(self, name, content, project_id, creator_id, state_id):
        document = Document(
            name=name,
            content=content,
            project_id=project_id,
            creator_id=creator_id,
            state_id=state_id,
            active=True,
        )
        return super().store_object_transactional(document)

    def delete_existing_recommendations(self, document_id):
        """Delete existing recommendations for a document."""
        db.session.query(DocumentRecommendation).filter(
            DocumentRecommendation.document_id == document_id
        ).delete()
        db.session.commit()

    def store_new_recommendations(self, document_id, recommendations):
        """Store new recommendations for a document."""
        for recommendation in recommendations:
            new_recommendation = DocumentRecommendation(
                document_id=document_id,
                recommendation_type=recommendation["type"],
                content=recommendation["content"],
            )
            db.session.add(new_recommendation)
        db.session.commit()
    
    def delete_existing_mentions_or_relations(self, document_id, step):
        """Delete mentions or relations for a specific step of a document."""
        if step == "mentions":
            db.session.query(Mention).filter(Mention.document_id == document_id).delete()
        elif step == "relations":
            db.session.query(Relation).filter(Relation.document_id == document_id).delete()
        db.session.commit()

    def store_new_mentions_or_relations(self, document_id, recommendations, step):
        """Store mentions or relations for a specific step of a document."""
        if step == "mentions":
            for mention in recommendations:
                new_mention = Mention(
                    document_id=document_id,
                    content=mention["content"],
                    start=mention["start"],
                    end=mention["end"],
                )
                db.session.add(new_mention)
        elif step == "relations":
            for relation in recommendations:
                new_relation = Relation(
                    document_id=document_id,
                    type=relation["type"],
                    source=relation["source"],
                    target=relation["target"],
                )
                db.session.add(new_relation)
        db.session.commit()