from app.models import UserTeam, Team
from app.repositories.base_repository import BaseRepository
from app.db import db


class TeamRepository(BaseRepository):

    def get_teams_by_user(self, user_id):
        return (
            db.session.query(Team)
            .join(UserTeam)
            .filter(UserTeam.user_id == user_id)
            .all()
        )
