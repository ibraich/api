from flask_restx import Namespace, Resource
import requests
from app.services.entity_service import entity_service
from werkzeug.exceptions import BadRequest, NotFound
from app.dtos import entity_output_list_dto, entity_input_dto, entity_output_dto
from flask import request, jsonify
import os

RECOMMENDATION_SYSTEM_URL = os.getenv("RECOMMENDATION_SYSTEM_URL", "http://localhost:8080/pipeline/docs")
ns = Namespace("entities", description="Entity related operations")


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityQueryResource(Resource):
    service = entity_service

    @ns.doc(description="Get Entities of document annotation")
    @ns.marshal_with(entity_output_list_dto)
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        response = self.service.get_entities_by_document_edit(document_edit_id)
        return response


@ns.route("/<int:entity_id>")
@ns.doc(params={"entity_id": "An Entity ID"})
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityDeletionResource(Resource):
    service = entity_service

    @ns.doc(description="Delete an entity")
    def delete(self, entity_id):
        response = self.service.delete_entity(entity_id)
        return response


@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(403, "Authorization required")
@ns.response(404, "Data not found")
class EntityCreationResource(Resource):
    service = entity_service

    @ns.doc(description="Create a new entity")
    @ns.marshal_with(entity_output_dto)
    @ns.expect(entity_input_dto)
    def post(self):
        response = self.service.create_entity(request.json)
        return response

@ns.route("/")
@ns.response(400, "Invalid input")
@ns.response(404, "Entity not found")
class EntityResource(Resource):
    @ns.expect(entity_input_dto)
    @ns.marshal_with(entity_output_dto)
    def post(self):
        """
        Detect entities in the given document.
        """
        payload = request.get_json()
        if not payload:
            raise BadRequest("Missing or invalid payload.")

        model_type = request.args.get('model_type', 'llm')
        if model_type != 'llm':
            raise BadRequest("Invalid model_type. Only 'llm' is supported.")

        model = request.args.get('model', 'gpt-4o-mini')
        temperature = request.args.get('temperature', 'none')

        try:
            # Forward the payload to the recommendation system
            response = requests.post(
                RECOMMENDATION_SYSTEM_URL,
                json={
                    "payload": payload,
                    "model_type": model_type,
                    "model": model,
                    "temperature": temperature,
                }
            )

            if response.status_code != 200:
                raise BadRequest(f"Recommendation system error: {response.text}")

            return response.json()
        except requests.RequestException as e:
            raise BadRequest(f"Failed to connect to recommendation system: {str(e)}")

@ns.route("/mentions")
@ns.response(400, "Invalid input")
@ns.response(404, "Mention not found")
class MentionResource(Resource):
    def post(self):
        """
        Handle mentions and transform indices into TokenIds.
        """
        payload = request.get_json()
        if not payload:
            raise BadRequest("Missing or invalid payload.")

        mentions = payload.get("mentions", [])
        for mention in mentions:
            start_idx = mention.get("startTokenDocumentIndex")
            end_idx = mention.get("endTokenDocumentIndex")
            if start_idx is None or end_idx is None:
                raise BadRequest("Missing token indices in mention.")

            # Transform indices into a list of TokenIds (mocked transformation for now)
            mention["TokenIds"] = list(range(start_idx, end_idx + 1))

        try:
            # Forward the transformed payload to the recommendation system
            response = requests.post(
                RECOMMENDATION_SYSTEM_URL,
                json=payload
            )

            if response.status_code != 200:
                raise BadRequest(f"Recommendation system error: {response.text}")

            return response.json()
        except requests.RequestException as e:
            raise BadRequest(f"Failed to connect to recommendation system: {str(e)}")

@ns.route("/<int:entity_id>")
@ns.doc(params={"entity_id": "An Entity ID"})
@ns.response(400, "Invalid input")
@ns.response(404, "Entity not found")
class EntityManagementResource(Resource):
    def get(self, entity_id):
        """
        Retrieve details of a specific entity by ID.
        """
        try:
            response = requests.get(f"{RECOMMENDATION_SYSTEM_URL}/{entity_id}")
            if response.status_code == 404:
                raise NotFound(f"Entity with ID {entity_id} not found.")
            return response.json()
        except requests.RequestException as e:
            raise BadRequest(f"Failed to retrieve entity: {str(e)}")

    def delete(self, entity_id):
        """
        Delete a specific entity by ID.
        """
        try:
            response = requests.delete(f"{RECOMMENDATION_SYSTEM_URL}/{entity_id}")
            if response.status_code == 404:
                raise NotFound(f"Entity with ID {entity_id} not found.")
            return jsonify({"message": "Entity deleted successfully.", "entity_id": entity_id})
        except requests.RequestException as e:
            raise BadRequest(f"Failed to delete entity: {str(e)}")