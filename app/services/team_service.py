from app.repositories.team_repository import TeamRepository


class TeamService:
    __team_repository: TeamRepository

    def __init__(self, team_repository):
        self.__team_repository = team_repository

    def get_teams_by_user(self, user_id):
        return self.__team_repository.get_teams_by_user(user_id)


team_service = TeamService(TeamRepository())
