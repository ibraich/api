from app.repositories.team_repository import TeamRepository
from app.services.user_service import UserService, user_service


class TeamService:
    __team_repository: TeamRepository
    user_service: UserService

    def __init__(self, team_repository, user_service):
        self.__team_repository = team_repository
        self.user_service = user_service

    def get_teams_by_user(self):
        user_id = 1  # self.user_service.get_logged_in_user_id()
        teams = self.__team_repository.get_teams_by_user(user_id)
        if teams is None:
            return {"teams": []}
        return {
            "teams": [
                {
                    "id": team.id,
                    "name": team.name,
                    "creator_id": team.creator_id,
                    "members": self.__get_team_members_by_team_id(team.id),
                }
                for team in teams
            ]
        }

    def __get_team_members_by_team_id(self, team_id):
        members = self.__team_repository.get_members_of_team(team_id)
        return [
            {"id": member.id, "username": member.username, "email": member.email}
            for member in members
        ]


team_service = TeamService(TeamRepository(), user_service)
