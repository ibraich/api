from app.models import UserTeam
from app.repositories.base_repository import BaseRepository


class UserTeamRepository(BaseRepository):

    def get_user_team_id(self, user_id):
        user_team = (
            self.get_session()
            .query(UserTeam)
            .filter(UserTeam.user_id == user_id)
            .first()
        )
        return user_team.team_id
