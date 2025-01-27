from app.models import (
    DocumentEdit,
    DocumentEditModelSettings,
    RecommendationModel,
    ModelStep,
)
from app.repositories.base_repository import BaseRepository


class DocumentEditRepository(BaseRepository):

    def create_document_edit(
        self,
        document_id,
        user_id,
        schema_id,
        model_mention=None,
        model_entities=None,
        model_relation=None,
    ):
        document_edit = DocumentEdit(
            document_id=document_id,
            user_id=user_id,
            schema_id=schema_id,
            state_id=1,
            active=True,
            mention_model_id=model_mention,
            entity_model_id=model_entities,
            relation_model_id=model_relation,
        )
        return super().store_object(document_edit)

    def get_document_edit_by_document(self, document_id, user_id):
        return (
            self.get_session()
            .query(DocumentEdit)
            .filter(DocumentEdit.document_id == document_id)
            .filter(DocumentEdit.user_id == user_id)
            .filter(DocumentEdit.active == True)
            .first()
        )

    def soft_delete_document_edit(self, document_edit_id):
        document_edit = (
            self.get_session()
            .query(DocumentEdit)
            .filter(DocumentEdit.id == document_edit_id, DocumentEdit.active == True)
            .first()
        )
        if not document_edit:
            return False
        document_edit.active = False
        return True

    def soft_delete_document_edits_by_document_id(self, document_id: int):
        (
            self.get_session()
            .query(DocumentEdit)
            .filter(
                DocumentEdit.document_id == document_id,
                DocumentEdit.active == True,
            )
            .update({DocumentEdit.active: False}, synchronize_session=False)
        )

    def bulk_soft_delete_edits(self, document_ids: list[int]):
        if not document_ids:
            return

        self.get_session().query(DocumentEdit).filter(
            DocumentEdit.document_id.in_(document_ids), DocumentEdit.active == True
        ).update({DocumentEdit.active: False}, synchronize_session=False)

    def get_document_edit_by_id(self, document_edit_id):
        return (
            self.get_session()
            .query(DocumentEdit)
            .filter(DocumentEdit.id == document_edit_id)
            .filter(DocumentEdit.active == True)
            .first()
        )

    def store_model_settings(self, document_edit_id, model_id, model_settings):
        if model_settings is None or model_id is None:
            return
        settings = []
        for model_setting in model_settings:
            settings.append(
                DocumentEditModelSettings(
                    document_edit_id=document_edit_id,
                    model_id=model_id,
                    key=model_setting["key"],
                    value=model_setting["value"],
                )
            )
        for setting in settings:
            super().store_object(setting)

    def get_document_edit_model(self, document_edit_id):
        return (
            self.get_session()
            .query(
                DocumentEditModelSettings.id.label("settings_id"),
                DocumentEditModelSettings.value,
                DocumentEditModelSettings.key,
                DocumentEdit.id.label("document_edit_id"),
                RecommendationModel.id,
                RecommendationModel.model_name,
                RecommendationModel.model_type,
                RecommendationModel.schema_id,
                RecommendationModel.model_step_id,
                ModelStep.type.label("model_step_name"),
            )
            .select_from(DocumentEdit)
            .join(
                RecommendationModel,
                (DocumentEdit.mention_model_id == RecommendationModel.id)
                | (DocumentEdit.entity_model_id == RecommendationModel.id)
                | (DocumentEdit.relation_model_id == RecommendationModel.id),
            )
            .join(
                ModelStep,
                RecommendationModel.model_step_id == ModelStep.id,
            )
            .outerjoin(
                DocumentEditModelSettings,
                DocumentEditModelSettings.recommendation_model_id
                == RecommendationModel.id,
            )
            .filter(DocumentEdit.id == document_edit_id)
            .all()
        )
