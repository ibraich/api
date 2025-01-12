from collections import namedtuple

from werkzeug.exceptions import Forbidden

from app.repositories.token_repository import TokenRepository
from app.services.token_service import TokenService, token_service
from tests.test_routes import BaseTestCase
from unittest.mock import patch
from app.services.user_service import UserService


class TokenFetchByDocumentTestCase(BaseTestCase):
    service: TokenService

    def setUp(self):
        super().setUp()
        self.service = token_service

    @patch.object(TokenService, "get_tokens_by_document")
    def test_get_tokens_by_document_endpoint_valid(
        self,
        get_tokens_mock,
    ):

        get_tokens_mock.return_value = {
            "tokens": [
                {
                    "id": 6,
                    "text": "Doc",
                    "document_index": 1,
                    "sentence_index": 1,
                    "pos_tag": "A",
                }
            ]
        }

        response = self.client.get(
            "/api/tokens/1",
            headers={"Content-Type": "application/json"},
        )

        # Assert the response is 200 for valid call
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.json,
            {
                "tokens": [
                    {
                        "id": 6,
                        "text": "Doc",
                        "document_index": 1,
                        "sentence_index": 1,
                        "pos_tag": "A",
                    }
                ]
            },
        )

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "check_user_document_accessible")
    @patch.object(TokenRepository, "get_tokens_by_document")
    def test_get_tokens_by_document_no_tokens(
        self, get_tokens_mock, check_access_mock, get_user_mock
    ):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1
        check_access_mock.return_value = None
        get_tokens_mock.return_value = None

        response = self.client.get("/api/tokens/1")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual({"tokens": []}, response.json)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "check_user_document_accessible")
    @patch.object(TokenRepository, "get_tokens_by_document")
    def test_get_tokens_by_document_no_access(
        self, get_tokens_mock, check_access_mock, get_user_mock
    ):
        # Mock the service to raise a BadRequest exception
        get_user_mock.return_value = 1
        check_access_mock.side_effect = Forbidden()
        get_tokens_mock.return_value = None

        response = self.client.get("/api/tokens/1")

        # Assert the response is 200
        self.assertEqual(403, response.status_code)

    @patch.object(UserService, "get_logged_in_user_id")
    @patch.object(UserService, "check_user_document_accessible")
    @patch.object(TokenRepository, "get_tokens_by_document")
    def test_get_projects_by_user_service_valid(
        self, get_tokens_mock, check_access_mock, get_user_mock
    ):
        get_user_mock.return_value = 1
        check_access_mock.return_value = None
        token_return = namedtuple(
            "Token",
            [
                "id",
                "text",
                "document_index",
                "sentence_index",
                "pos_tag",
            ],
        )
        get_tokens_mock.return_value = [token_return(6, "Doc", 1, 1, "A")]

        response = self.client.get("/api/tokens/1")

        # Assert the response is 200
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "tokens": [
                    {
                        "id": 6,
                        "text": "Doc",
                        "document_index": 1,
                        "sentence_index": 1,
                        "pos_tag": "A",
                    }
                ]
            },
            response.json,
        )
