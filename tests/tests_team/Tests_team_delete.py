import unittest
from unittest.mock import MagicMock
from werkzeug.exceptions import NotFound
from app.services.team_service import TeamService
from app.repositories.team_repository import TeamRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_edit_repository import DocumentEditRepository

class TestTeamService(unittest.TestCase):
    def setUp(self):
        self.mock_db_session = MagicMock()
        self.mock_team_repo = MagicMock(spec=TeamRepository)
        self.mock_project_repo = MagicMock(spec=ProjectRepository)
        self.mock_document_repo = MagicMock(spec=DocumentRepository)
        self.mock_document_edit_repo = MagicMock(spec=DocumentEditRepository)

        self.team_service = TeamService(self.mock_db_session)
        self.team_service.team_repository = self.mock_team_repo
        self.team_service.project_repository = self.mock_project_repo
        self.team_service.document_repository = self.mock_document_repo
        self.team_service.document_edit_repository = self.mock_document_edit_repo

    def test_delete_team_logically_team_not_found(self):
        # Arrange
        self.mock_team_repo.get_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotFound):
            self.team_service.delete_team_logically(1)

        self.mock_team_repo.get_by_id.assert_called_once_with(1)

    def test_delete_team_logically_success(self):
        # Arrange
        self.mock_team_repo.get_by_id.return_value = MagicMock()
        self.mock_project_repo.get_ids_by_team_id.return_value = [10, 20]
        self.mock_document_repo.get_ids_by_project_ids.return_value = [100, 200]
        self.mock_document_edit_repo.get_ids_by_document_ids.return_value = [1000, 2000]

        # Act
        self.team_service.delete_team_logically(1)

        # Assert
        self.mock_team_repo.get_by_id.assert_called_once_with(1)
        self.mock_team_repo.mark_inactive.assert_called_once_with(1)
        self.mock_project_repo.get_ids_by_team_id.assert_called_once_with(1)
        self.mock_project_repo.mark_inactive_bulk.assert_called_once_with([10, 20])
        self.mock_document_repo.get_ids_by_project_ids.assert_called_once_with([10, 20])
        self.mock_document_repo.mark_inactive_bulk.assert_called_once_with([100, 200])
        self.mock_document_edit_repo.get_ids_by_document_ids.assert_called_once_with([100, 200])
        self.mock_document_edit_repo.mark_inactive_bulk.assert_called_once_with([1000, 2000])
        self.mock_db_session.commit.assert_called_once()

    def test_delete_team_logically_no_projects(self):
        # Arrange
        self.mock_team_repo.get_by_id.return_value = MagicMock()
        self.mock_project_repo.get_ids_by_team_id.return_value = []

        # Act
        self.team_service.delete_team_logically(1)

        # Assert
        self.mock_team_repo.get_by_id.assert_called_once_with(1)
        self.mock_team_repo.mark_inactive.assert_called_once_with(1)
        self.mock_project_repo.get_ids_by_team_id.assert_called_once_with(1)
        self.mock_project_repo.mark_inactive_bulk.assert_not_called()
        self.mock_document_repo.get_ids_by_project_ids.assert_not_called()
        self.mock_document_edit_repo.get_ids_by_document_ids.assert_not_called()
        self.mock_db_session.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
