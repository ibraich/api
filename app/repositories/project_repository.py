from app.models import Project, Document, DocumentEdit, Team, UserTeam
from app.repositories.base_repository import BaseRepository
from sqlalchemy import exc
from app.db import db


class ProjectRepository(BaseRepository):
    def create_project(self, name, creator_id, team_id, schema_id):
        project = Project(
            name=name,
            creator_id=creator_id,
            team_id=team_id,
            schema_id=schema_id,
        )
        super().store_object(project)
        return project

    def get_team_id_by_document_edit_id(self, document_edit_id):
        project = (
            db.session.query(Project)
            .join(Document, Document.project_id == Project.id)
            .join(DocumentEdit, DocumentEdit.document_id == Document.id)
            .filter(DocumentEdit.id == document_edit_id)
            .first()
        )
        return project.team_id

    def get_projects_by_team(self, team_id):
        return db.session.query(Project).filter(Project.team_id == team_id).all()

    def get_project_by_id(self, project_id):
        return db.session.query(Project).filter(Project.id == project_id).first()

    def get_projects_by_user(self, user_id):
        return (
            db.session.query(
                Project.id,
                Project.name,
                Project.creator_id,
                Project.team_id,
                Project.schema_id,
                Team.name.label("team_name"),
            )
            .select_from(UserTeam)
            .join(Team, Team.id == UserTeam.team_id)
            .join(Project, Project.team_id == Team.id)
            .filter(UserTeam.user_id == user_id)
            .all()
        )
