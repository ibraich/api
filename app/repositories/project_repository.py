from app.models import Project, Document, DocumentEdit, Team, UserTeam, Schema
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository):

    def __init__(self, db_session):
        self.db_session = db_session

    def create_project(self, name, creator_id, team_id, schema_id):
        project = Project(
            name=name,
            creator_id=creator_id,
            team_id=team_id,
            schema_id=schema_id,
            active=True,
        )
        super().store_object(project)
        return project

    def get_team_id_by_document_edit_id(self, document_edit_id):
        project = (
            self.get_session()
            .query(Project)
            .join(Document, Document.project_id == Project.id)
            .join(DocumentEdit, DocumentEdit.document_id == Document.id)
            .filter(DocumentEdit.id == document_edit_id)
            .first()
        )
        return project.team_id

    def get_projects_by_team(self, team_id):
        return (
            self.get_session()
            .query(Project)
            .filter(Project.team_id == team_id)
            .filter(Project.active == True)
            .all()
        )

    def get_project_by_id(self, project_id):
        return (
            self.get_session()
            .query(
                Project.id,
                Project.name,
                Project.creator_id,
                Project.team_id,
                Project.schema_id,
                Schema.name.label("schema_name"),
                Team.name.label("team_name"),
            )
            .select_from(UserTeam)
            .join(Team, Team.id == UserTeam.team_id)
            .join(Project, Project.team_id == Team.id)
            .join(Schema, Schema.id == Project.schema_id)
            .filter(Project.id == project_id)
            .first()
        )

    def get_projects_by_user(self, user_id):
        return (
            self.get_session()
            .query(
                Project.id,
                Project.name,
                Project.creator_id,
                Project.team_id,
                Project.schema_id,
                Schema.name.label("schema_name"),
                Team.name.label("team_name"),
            )
            .select_from(UserTeam)
            .join(Team, Team.id == UserTeam.team_id)
            .join(Project, Project.team_id == Team.id)
            .join(Schema, Schema.id == Project.schema_id)
            .filter(UserTeam.user_id == user_id)
            .filter(Project.active == True)
            .all()
        )

    def soft_delete_project(self, project_id):
        project = (
            self.get_session()
            .query(Project)
            .filter(Project.id == project_id, Project.active == True)
            .first()
        )
        if not project:
            return False

        project.active = False
        return True

    def get_ids_by_team_id(self, team_id: int):
        return [p.id for p in self.db_session.query(Project).filter_by(team_id=team_id, active=True).all()]

    def mark_inactive_bulk(self, project_ids: list):
        self.db_session.query(Project).filter(Project.id.in_(project_ids)).update({"active": False}, synchronize_session="fetch")