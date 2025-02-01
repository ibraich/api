from app.models import UserTeam, Team, User, Project
from app.repositories.base_repository import BaseRepository


class TeamRepository(BaseRepository):

    def get_teams_by_user(self, user_id):
        return (
            self.get_session()
            .query(Team.id, Team.name, Team.creator_id)
            .join(UserTeam, UserTeam.team_id == Team.id)
            .filter(UserTeam.user_id == user_id)
            .filter(Team.active == True)
            .all()
        )

    def get_team_by_id(self, team_id):
        return (
            self.get_session()
            .query(Team.id, Team.name, Team.creator_id)
            .filter(Team.id == team_id)
            .filter(Team.active == True)
            .first()
        )

    def get_members_of_team(self, team_id):
        return (
            self.get_session()
            .query(User.id, User.username, User.email)
            .select_from(UserTeam)
            .join(User, User.id == UserTeam.user_id)
            .filter(UserTeam.team_id == team_id)
            .all()
        )

    def create_team(self, name, creator_id):
        team = Team(
            name=name,
            creator_id=creator_id,
            active=True,
        )
        super().store_object(team)
        return team

    def add_user(self, team_id, user_id):
        userteam = UserTeam(team_id=team_id, user_id=user_id)
        super().store_object(userteam)
        return userteam

    def remove_user(self, team_id, user_id):
        userteam = (
            self.get_session()
            .query(UserTeam)
            .filter(UserTeam.team_id == team_id, UserTeam.user_id == user_id)
            .first()
        )
        self.get_session().delete(userteam)

    def get_team_by_project_id(self, project_id):

        project = (
            self.get_session()
            .query(Project)
            .filter(Project.id == project_id)
            .filter(Project.active == True)
            .first()
        )
        if project:
            return project.team_id
        return None

    def update_team_name(self, team_id: int, new_name: str):
        """Update a team's name in the database."""
        team = Team.query.filter_by(id=team_id, active=True).first()
        if not team:
            return False

        team.name = new_name
        return team

    def get_team_by_name(self, name):
        return (
            self.get_session()
            .query(Team)
            .filter(Team.name == name)
            .filter(Team.active == True)
            .first()
        )
    
    def __init__(self, db_session):
        self.db_session = db_session

    def soft_delete_team(self, team_id):
        # Perform a bulk update to mark the team as inactive
        team = self.db_session.query(Team).filter_by(id=team_id, active=True).first()
        if not team:
            return False

        team.active = False
        self.db_session.commit()
        return True
