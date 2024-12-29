from app.models import UserTeam, Team, User
from app.repositories.base_repository import BaseRepository
from app.db import db


class TeamRepository(BaseRepository):

    def get_teams_by_user(self, user_id):
        return (
            db.session.query(Team.id, Team.name, Team.creator_id)
            .join(UserTeam, UserTeam.team_id == Team.id)
            .filter(UserTeam.user_id == user_id)
            .all()
        )

    def get_members_of_team(self, team_id):
        return (
            db.session.query(User.id, User.username, User.email)
            .select_from(UserTeam)
            .join(User, User.id == UserTeam.user_id)
            .filter(UserTeam.team_id == team_id)
            .all()
        )
