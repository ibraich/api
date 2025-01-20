import unittest
from unittest.mock import MagicMock, patch
from werkzeug.exceptions import BadRequest, NotFound
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_user_repository = MagicMock(spec=UserRepository)
        self.user_service = UserService(user_repository=self.mock_user_repository)

    def test_update_user_data_success(self):
        # Arrange
        user_id = 1
        username = "new_username"
        email = "new_email@example.com"
        password = "new_password"
        mock_user = {
            "id": user_id,
            "username": username,
            "email": email,
        }

        self.mock_user_repository.update_user_data.return_value = mock_user

        # Act
        result = self.user_service.update_user_data(
            user_id=user_id, username=username, email=email, password=password
        )

        # Assert
        self.mock_user_repository.update_user_data.assert_called_once_with(
            user_id=user_id, username=username, email=email, password=password
        )
        self.assertEqual(result, mock_user)

    def test_update_user_data_no_fields_provided(self):
        # Arrange
        user_id = 1

        # Act & Assert
        with self.assertRaises(BadRequest):
            self.user_service.update_user_data(user_id=user_id)

    def test_update_user_data_user_not_found(self):
        # Arrange
        user_id = 1
        self.mock_user_repository.update_user_data.side_effect = NotFound(
            "User not found"
        )

        # Act & Assert
        with self.assertRaises(NotFound):
            self.user_service.update_user_data(user_id=user_id, username="test")


if __name__ == "__main__":
    unittest.main()
