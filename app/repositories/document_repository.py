from app.models import (
    Document,
    DocumentState,
    Project,
    DocumentEditState,
    DocumentEdit,
    Team,
    User,
    UserTeam,
    DocumentRecommendation,
    Schema,
)
from app.repositories.base_repository import BaseRepository
from sqlalchemy import and_, literal


class DocumentRepository(BaseRepository):
    DOCUMENT_STATE_ID_FINISHED = 3

    def get_documents_by_user(self, user_id):
        return (
            self.get_session()
            .query(
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
                DocumentState.id.label("document_state_id"),
                DocumentState.type.label("document_state_type"),
                User.id.label("creator_id"),
                User.email.label("email"),
                User.username.label("username"),
            )
            .select_from(UserTeam)
            .filter(UserTeam.user_id == user_id)
            .filter(Document.active == True)
            .join(Team, UserTeam.team_id == Team.id)
            .join(Project, Team.id == Project.team_id)
            .join(Document, Project.id == Document.project_id)
            .join(DocumentState, DocumentState.id == Document.state_id)
            .join(Schema, Schema.id == Project.schema_id)
            .join(User, User.id == Document.creator_id)
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

    def get_document_by_id_without_edit(self, document_id):
        return (
            self.get_session()
            .query(
                Document.id,
                Document.content,
                Document.name,
                Document.project_id,
                Project.name.label("project_name"),
                Project.schema_id,
                Schema.name.label("schema_name"),
                Team.name.label("team_name"),
                Team.id.label("team_id"),
                DocumentState.id.label("document_state_id"),
                DocumentState.type.label("document_state_type"),
                User.id.label("creator_id"),
                User.email.label("email"),
                User.username.label("username"),
                literal(None).label("document_edit_id"),
                literal(None).label("document_edit_state"),
            )
            .filter(Document.id == document_id)
            .filter(Document.active == True)
            .join(Project, Project.id == Document.project_id)
            .join(Team, Project.team_id == Team.id)
            .join(DocumentState, DocumentState.id == Document.state_id)
            .join(Schema, Schema.id == Project.schema_id)
            .join(User, User.id == Document.creator_id)
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
        return super().store_object(document)

    def soft_delete_document(self, document_id: int):
        document = (
            self.get_session()
            .query(Document)
            .filter(Document.id == document_id, Document.active == True)
            .first()
        )
        if not document:
            return False

        document.active = False
        return True

    def bulk_soft_delete_documents_by_project_id(self, project_id: int) -> list[int]:
        # Step 1: Get all doc IDs first
        doc_ids = (
            self.get_session()
            .query(Document.id)
            .filter(Document.project_id == project_id, Document.active == True)
            .all()
        )  # returns list of tuples like [(1,), (2,)...]
        doc_ids = [row[0] for row in doc_ids]

        if not doc_ids:
            return []

        # Step 2: Bulk update
        self.get_session().query(Document).filter(Document.id.in_(doc_ids)).update(
            {Document.active: False}, synchronize_session=False
        )

        return doc_ids

    def get_all_document_edits_by_document(self, document_id):
        return (
            self.get_session()
            .query(DocumentEdit)
            .filter(DocumentEdit.document_id == document_id)
            .filter(DocumentEdit.active == True)
            .all()
        )

    def get_all_document_edits_with_user_by_document(self, document_id):
        return (
            self.get_session()
            .query(
                DocumentEdit.id.label("edit_id"),
                User.id.label("user_id"),
                User.email.label("user_email"),
                User.username.label("user_username"),
                DocumentEditState.id.label("state_id"),
                DocumentEditState.type.label("state_type"),
            )
            .join(User, User.id == DocumentEdit.user_id)
            .join(DocumentEditState, DocumentEditState.id == DocumentEdit.state_id)
            .filter(DocumentEdit.document_id == document_id)
            .filter(DocumentEdit.active == True)
            .all()
        )

    def fetch_document_by_id(self, document_id):
        return self.get_session().query(Document).filter_by(id=document_id).first()

    def fetch_document_edits(self, document_id):
        return self.get_session().query(DocumentEdit).filter_by(document_id=document_id).all()
