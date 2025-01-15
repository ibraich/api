import unittest
from unittest.mock import MagicMock
from app.services.relation_services import RelationService

class TestRelationService(unittest.TestCase):
    def setUp(self):
        # Mocking the repository
        self.relation_repository = MagicMock()
        self.relation_service = RelationService(self.relation_repository)

    def test_accept_relation_success(self):
        relation_id = 1
        document_edit_id = 2
        relation_mock = MagicMock(
            id=relation_id,
            document_edit_id=document_edit_id,
            isShownRecommendation=True,
            tag="relation-tag",
            isDirected=True,
            mention_head_id=10,
            mention_tail_id=20
        )

        # Mocking repository methods
        self.relation_repository.get_relation_by_id.return_value = relation_mock

        # Call the service method
        result = self.relation_service.accept_relation(relation_id, document_edit_id)

        # Assertions
        self.relation_repository.get_relation_by_id.assert_called_once_with(relation_id)
        self.relation_repository.create_relation.assert_called_once_with(
            tag="relation-tag",
            document_edit_id=document_edit_id,
            is_directed=True,
            mention_head_id=10,
            mention_tail_id=20,
            document_recommendation_id=None,
            is_shown_recommendation=False,
        )
        self.relation_repository.update_is_shown_recommendation.assert_called_once_with(relation_id, False)
        self.assertIsNotNone(result)
    def test_accept_relation_invalid_document_edit_id(self):
        relation_id = 1
        document_edit_id = 2
        relation_mock = MagicMock(
            id=relation_id,
            document_edit_id=99,
            isShownRecommendation=True
        )
        self.relation_repository.get_relation_by_id.return_value = relation_mock
        with self.assertRaises(ValueError):
            self.relation_service.accept_relation(relation_id, document_edit_id)
    def test_reject_relation_success(self):
        relation_id = 1
        document_edit_id = 2
        relation_mock = MagicMock(
            id=relation_id,
            document_edit_id=document_edit_id,
            isShownRecommendation=True
        )
        # Mocking repository methods
        self.relation_repository.get_relation_by_id.return_value = relation_mock
        # Call the service method
        result = self.relation_service.reject_relation(relation_id, document_edit_id)
        # Assertions
        self.relation_repository.get_relation_by_id.assert_called_once_with(relation_id)
        self.relation_repository.update_is_shown_recommendation.assert_called_once_with(relation_id, False)
        self.assertIsNotNone(result)
    def test_reject_relation_invalid_state(self):
        relation_id = 1
        document_edit_id = 2
        relation_mock = MagicMock(
            id=relation_id,
            document_edit_id=document_edit_id,
            isShownRecommendation=False
        )
        self.relation_repository.get_relation_by_id.return_value = relation_mock
        with self.assertRaises(ValueError):
            self.relation_service.reject_relation(relation_id, document_edit_id)