from app.models import (
    Document,
    DocumentState,
    DocumentRecommendation,
    Project,
    DocumentEditState,
    DocumentEdit,
    Mention,
    Relation,
    Team,
    User,
    UserTeam,
    DocumentRecommendation,
    Schema,
)
from app.repositories.base_repository import BaseRepository
from sqlalchemy import and_
from app.db import db, Session


class DocumentRepository(BaseRepository):
    DOCUMENT_STATE_ID_FINISHED = 3

    def __init__(self):
        self.db_session = db.session

    def get_documents_by_user(self, user_id):
        return (
            db.session.query(
                Document.id,
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Schema.name.label("schema_name"),
                Team.name.label("team_name"),
                Team.id.label("team_id"),
                DocumentEditState.type.label("document_edit_state"),
                DocumentEdit.id.label("document_edit_id"),
            )
            .select_from(User)
            .filter(User.id == user_id)
            .filter(Document.active == True)
            .join(UserTeam, User.id == UserTeam.user_id)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Team.id == Project.team_id)
            .join(Document, Project.id == Document.project_id)
            .join(DocumentState, DocumentState.id == Document.state_id)
            .join(Schema, Schema.id == Project.schema_id)
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
                Schema.name.label("schema_name"),
                Project.team_id,
                DocumentRecommendation.id.label("document_recommendation_id"),
            )
            .select_from(Document)
            .filter(Document.id == document_id)
            .filter(Document.active == True)
            .join(Project, Project.id == Document.project_id)
            .join(Schema, Schema.id == Project.schema_id)
            .outerjoin(
                DocumentRecommendation,
                and_(
                    Document.id == DocumentRecommendation.document_id,
                    DocumentRecommendation.document_edit_id.is_(None),
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

    def soft_delete_document(self, document_id: int) -> bool:
        """
        Setzt das 'active'-Flag eines Dokuments auf False.
        :param document_id: ID des Dokuments
        :return: True, wenn erfolgreich, False, wenn das Dokument nicht gefunden wurde
        """
        document = (
            self.db_session.query(Document)
            .filter(Document.id == document_id, Document.active == True)
            .first()
        )
        if not document:
            return False
        document.active = False
        self.db_session.commit()
        return True

    def bulk_soft_delete_documents_by_project_id(self, project_id: int) -> list[int]:
        """
        Setzt das 'active'-Flag aller Dokumente eines Projekts auf False.
        :param project_id: ID des Projekts
        :return: Liste der IDs der deaktivierten Dokumente
        """
        # Schritt 1: Dokument-IDs abrufen
        doc_ids = self.db_session.query(Document.id).filter(
            Document.project_id == project_id,
            Document.active == True
        ).all()
        doc_ids = [row[0] for row in doc_ids]

        if not doc_ids:
            return []

        # Schritt 2: Bulk-Update durchführen
        self.db_session.query(Document).filter(
            Document.id.in_(doc_ids)
        ).update({Document.active: False}, synchronize_session=False)
        self.db_session.commit()

        return doc_ids
