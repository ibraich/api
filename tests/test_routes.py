import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.config import TestingConfig
from app.repositories.document_edit_repository import DocumentEditRepository
from app.repositories.document_recommendation_repository import (
    DocumentRecommendationRepository,
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.entity_repository import EntityRepository
from app.repositories.mention_repository import MentionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.relation_repository import RelationRepository
from app.repositories.schema_repository import SchemaRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.token_mention_repository import TokenMentionRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.services.document_edit_service import DocumentEditService
from app.services.document_recommendation_service import DocumentRecommendationService
from app.services.document_service import DocumentService
from app.services.entity_mention_service import EntityMentionService
from app.services.entity_service import EntityService
from app.services.f1_score_service import F1ScoreService
from app.services.import_service import ImportService
from app.services.mention_services import MentionService
from app.services.project_service import ProjectService
from app.services.relation_mention_service import RelationMentionService
from app.services.relation_services import RelationService
from app.services.schema_service import SchemaService
from app.services.team_service import TeamService
from app.services.token_mention_service import TokenMentionService
from app.services.token_service import TokenService
from app.services.user_service import UserService


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.patcher = patch(
            "flask_jwt_extended.view_decorators.verify_jwt_in_request",
            return_value=None,
        )
        self.mock_function = self.patcher.start()

        self.document_edit_service = MagicMock(spec=DocumentEditService)
        self.document_recommendation_service = MagicMock(
            spec=DocumentRecommendationService
        )
        self.document_service = MagicMock(spec=DocumentService)
        self.entity_mention_service = MagicMock(spec=EntityMentionService)
        self.entity_service = MagicMock(spec=EntityService)
        self.import_service = MagicMock(spec=ImportService)
        self.mention_service = MagicMock(spec=MentionService)
        self.project_service = MagicMock(spec=ProjectService)
        self.relation_mention_service = MagicMock(spec=RelationMentionService)
        self.relation_service = MagicMock(spec=RelationService)
        self.schema_service = MagicMock(spec=SchemaService)
        self.team_service = MagicMock(spec=TeamService)
        self.token_mention_service = MagicMock(spec=TokenMentionService)
        self.token_service = MagicMock(spec=TokenService)
        self.user_service = MagicMock(spec=UserService)
        self.f1_score_service: F1ScoreService = MagicMock(spec=F1ScoreService)

        self.document_edit_repository = MagicMock(spec=DocumentEditRepository)
        self.document_recommendation_repository = MagicMock(
            spec=DocumentRecommendationRepository
        )
        self.document_repository = MagicMock(spec=DocumentRepository)
        self.entity_repository = MagicMock(spec=EntityRepository)
        self.mention_repository = MagicMock(spec=MentionRepository)
        self.project_repository = MagicMock(spec=ProjectRepository)
        self.relation_repository = MagicMock(spec=RelationRepository)
        self.schema_repository = MagicMock(spec=SchemaRepository)
        self.team_repository = MagicMock(spec=TeamRepository)
        self.token_mention_repository = MagicMock(spec=TokenMentionRepository)
        self.token_repository = MagicMock(spec=TokenRepository)
        self.user_repository = MagicMock(spec=UserRepository)

    def tearDown(self):
        self.patcher.stop()


class MentionBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service: MentionService = MentionService(
            self.mention_repository,
            self.token_mention_service,
            self.relation_mention_service,
            self.entity_mention_service,
            self.token_service,
            self.schema_service,
        )


class EntityBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service: EntityService = EntityService(
            self.entity_repository,
            self.schema_service,
            self.entity_mention_service,
            self.mention_service,
        )


class DocumentEditBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service: DocumentEditService = DocumentEditService(
            self.document_edit_repository,
            self.document_recommendation_service,
            self.token_service,
            self.mention_service,
            self.relation_service,
            self.schema_service,
            self.entity_service,
            self.f1_score_service,
        )


class ProjectBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.service: ProjectService = ProjectService(
            self.project_repository,
            self.user_service,
            self.schema_service,
            self.document_service,
        )
