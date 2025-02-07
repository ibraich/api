import unittest
from unittest.mock import MagicMock, patch
from werkzeug.exceptions import BadRequest, NotFound
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_user_repository = MagicMock(spec=UserRepository)
        self.user_service = UserService(user_repository=self.mock_user_repository)

    def test_update_user_data_no_fields_provided(self):
        # Arrange
        user_id = 1

        # Act & Assert
        with self.assertRaises(BadRequest):
            self.user_service.update_user_data(user_id=user_id)


if __name__ == "__main__":
    unittest.main()
