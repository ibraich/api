import requests
from flask import current_app
from werkzeug.exceptions import BadRequest

from app.services.document_edit_service import (
    DocumentEditService,
    document_edit_service,
)
from app.services.schema_service import SchemaService, schema_service


class TrainService:
    schema_service: SchemaService
    document_edit_service: DocumentEditService

    def __init__(self, schema_service, document_edit_service):
        self.schema_service = schema_service
        self.document_edit_service = document_edit_service

    def train_model_for_schema(
        self, schema_id, model_name, model_type, step, document_edits, settings
    ):
        """
        Trains a recommendation model for given schema id.
        Stores model information in the database.

        :param schema_id: Schema ID to train model for
        :param model_name: Name of the model
        :param model_type: Type of the model
        :param step: Step for which model can be used
        :param document_edits: Document edit IDs to use as training input
        :param settings: Settings for model training
        :return: model_train_output_list_dto
        :raises BadRequest: If model name already exists or training failed
        """
        duplicate = self.schema_service.get_model_by_name(model_name)
        if duplicate is not None:
            raise BadRequest("Model Name already exists")

        if step not in ["MENTIONS", "ENTITIES", "RELATIONS"]:
            raise BadRequest("Step must be mention, entity or relation")

        # Query parameter for training endpoint
        params = {}
        for setting in settings:
            params[setting["key"]] = setting["value"]
        params["model_type"] = model_type
        params["name"] = model_name

        schema = self.schema_service.get_schema_by_id(schema_id)

        document_edits = (
            self.document_edit_service.get_document_edits_for_schema_training(
                document_edits, schema_id
            )
        )

        request_body = {
            "schema": schema,
            "documents": document_edits,
        }
        pipeline_step_mapping = {
            "MENTIONS": "mention",
            "ENTITIES": "entity",
            "RELATIONS": "relation",
        }
        url = (
            current_app.config.get("PIPELINE_URL")
            + "/train/"
            + pipeline_step_mapping[step]
        )
        headers = {"Content-Type": "application/json"}

        train_response = requests.post(
            url=url, headers=headers, params=params, json=request_body
        )
        if train_response.status_code != 200:
            raise BadRequest("Failed to train model: " + train_response.text)

        # Store model in database
        models = self.schema_service.add_model_to_schema(
            schema_id, model_name, model_type, [step]
        )
        return {
            "models": [
                {
                    "id": model.id,
                    "name": model.model_name,
                    "type": model.model_type,
                    "step": {
                        "id": model.model_step_id,
                        "type": model.model_step_name,
                    },
                    "schema_id": model.schema_id,
                }
                for model in models
            ]
        }


train_service = TrainService(schema_service, document_edit_service)
