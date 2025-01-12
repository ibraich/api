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

    def __init__(self, db_session=None):
        """
        Initialisiert das Repository mit einer DB-Session.
        :param db_session: Optional, benutzerdefinierte DB-Session.
        """
        self.db_session = db_session or db.session
     # Allgemeine Löschmethode
    def delete_entries(self, model, filter_conditions: dict):
        """
        Generische Methode zum Löschen von Einträgen basierend auf Modell und Filterbedingungen.
        :param model: Datenbankmodell
        :param filter_conditions: Bedingungen als Dictionary (z. B. {"document_id": 1})
        """
        try:
            query = self.db_session.query(model)
            for field, value in filter_conditions.items():
                query = query.filter(getattr(model, field) == value)
            query.delete()
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"Fehler beim Löschen von {model.__name__}: {e}")

    # Allgemeine Speichermethode
    def store_entries(self, model, entries, mapper_function):
        """
        Generische Methode zum Speichern von Einträgen in die Datenbank.
        :param model: Datenbankmodell
        :param entries: Liste der zu speichernden Einträge
        :param mapper_function: Funktion, die einen Eintrag in ein Modell-Objekt umwandelt
        """
        try:
            for entry in entries:
                self.db_session.add(mapper_function(entry))
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"Fehler beim Speichern von {model.__name__}: {e}")

    # Empfehlungen verwalten
    def delete_recommendations(self, document_id):
        """Lösche alle Empfehlungen für ein Dokument."""
        self.delete_entries(DocumentRecommendation, {"document_id": document_id})

    def store_recommendations(self, document_id, recommendations):
        """Speichere neue Empfehlungen für ein Dokument."""
        def recommendation_mapper(recommendation):
            return DocumentRecommendation(
                document_id=document_id,
                recommendation_type=recommendation["type"],
                content=recommendation["content"],
            )
        self.store_entries(DocumentRecommendation, recommendations, recommendation_mapper)

    # Erwähnungen und Relationen verwalten
    def delete_mentions_or_relations(self, document_id, step):
        """
        Lösche Erwähnungen oder Relationen für ein spezifisches Dokument.
        :param document_id: ID des Dokuments
        :param step: "mentions" oder "relations"
        """
        model = Mention if step == "mentions" else Relation
        self.delete_entries(model, {"document_id": document_id})

    def store_mentions_or_relations(self, document_id, entries, step):
        """
        Speichere Erwähnungen oder Relationen für ein Dokument.
        :param document_id: ID des Dokuments
        :param entries: Einträge zum Speichern
        :param step: "mentions" oder "relations"
        """
        if step == "mentions":
            def mention_mapper(entry):
                return Mention(
                    document_id=document_id,
                    content=entry["content"],
                    start=entry["start"],
                    end=entry["end"],
                )
            self.store_entries(Mention, entries, mention_mapper)
        elif step == "relations":
            def relation_mapper(entry):
                return Relation(
                    document_id=document_id,
                    type=entry["type"],
                    source=entry["source"],
                    target=entry["target"],
                )
            self.store_entries(Relation, entries, relation_mapper)

    # Soft-Deletion eines Dokuments
    def soft_delete_document(self, document_id: int) -> bool:
        """
        Setzt das 'active'-Flag eines Dokuments auf False.
        :param document_id: ID des Dokuments
        :return: True, wenn erfolgreich, False, wenn das Dokument nicht gefunden wurde
        """
        document = self.db_session.query(Document).filter(
            Document.id == document_id,
            Document.active == True
        ).first()
        if not document:
            return False
        document.active = False
        self.db_session.commit()
        return True

    # Soft-Deletion für mehrere Dokumente eines Projekts
    def bulk_soft_delete_documents_by_project_id(self, project_id: int) -> list[int]:
        """
        Setzt das 'active'-Flag aller Dokumente eines Projekts auf False.
        :param project_id: ID des Projekts
        :return: Liste der IDs der deaktivierten Dokumente
        """
        doc_ids = self.db_session.query(Document.id).filter(
            Document.project_id == project_id,
            Document.active == True
        ).all()
        doc_ids = [row[0] for row in doc_ids]

        if not doc_ids:
            return []

        self.db_session.query(Document).filter(
            Document.id.in_(doc_ids)
        ).update({Document.active: False}, synchronize_session=False)
        self.db_session.commit()

        return doc_ids