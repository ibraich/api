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
    def __init__(self, db_session):
        self.db_session = db_session
        
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

    def delete_existing_entries(self, model, document_id):
        """Generische Methode zum Löschen von Einträgen basierend auf dem Modell und der Dokument-ID."""
        try:
            self.db_session.query(model).filter(model.document_id == document_id).delete()
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"Fehler beim Löschen von Einträgen: {e}")

    def store_entries(self, model, entries, document_id, mapper_function):
        """
        Generische Methode zum Speichern von Einträgen.
        
        :param model: Datenbankmodell.
        :param entries: Liste der Einträge.
        :param document_id: ID des Dokuments.
        :param mapper_function: Funktion, die einen Eintrag in ein Modell-Objekt umwandelt.
        """
        try:
            for entry in entries:
                new_entry = mapper_function(entry, document_id)
                self.db_session.add(new_entry)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"Fehler beim Speichern von Einträgen: {e}")

    def delete_recommendations(self, document_id):
        """Lösche alle Empfehlungen für ein Dokument."""
        self.delete_existing_entries(DocumentRecommendation, document_id)

    def store_recommendations(self, document_id, recommendations):
        """Speichere neue Empfehlungen für ein Dokument."""
        def recommendation_mapper(recommendation, document_id):
            return DocumentRecommendation(
                document_id=document_id,
                recommendation_type=recommendation["type"],
                content=recommendation["content"],
            )
        self.store_entries(DocumentRecommendation, recommendations, document_id, recommendation_mapper)

    def delete_mentions_or_relations(self, document_id, step):
        """Lösche Erwähnungen oder Relationen für ein spezifisches Dokument."""
        model = Mention if step == "mentions" else Relation
        self.delete_existing_entries(model, document_id)

    def store_mentions_or_relations(self, document_id, entries, step):
        """Speichere Erwähnungen oder Relationen für ein spezifisches Dokument."""
        if step == "mentions":
            def mention_mapper(entry, document_id):
                return Mention(
                    document_id=document_id,
                    content=entry["content"],
                    start=entry["start"],
                    end=entry["end"],
                )
            self.store_entries(Mention, entries, document_id, mention_mapper)
        elif step == "relations":
            def relation_mapper(entry, document_id):
                return Relation(
                    document_id=document_id,
                    type=entry["type"],
                    source=entry["source"],
                    target=entry["target"],
                )
            self.store_entries(Relation, entries, document_id, relation_mapper)