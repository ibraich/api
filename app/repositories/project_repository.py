from app.models import Project
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
        try:
            super().store_object(project)
            return {"message": "Success", "project": project}, 200
        except exc.IntegrityError:
            response = {
                "message": "Projectname already exists",
                "project_name": project.name,
            }
            return response, 400
        except exc.SQLAlchemyError:
            response = {"message": "Creating project not possible"}
            return response, 400

    def get_projects_by_team(self, team_id):
        return db.session.query(Project).filter(Project.team_id == team_id).all()
