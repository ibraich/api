from flask_restx import Namespace, Resource
from app.services.entity_service import entity_service
from werkzeug.exceptions import BadRequest

ns = Namespace("entities", description="Entity related operations")


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
class EntityQueryResource(Resource):
    service = entity_service

    @ns.doc(description="Get Entities of document annotation")
    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        document_edit_id = int(document_edit_id)

        response = self.service.get_entities_by_document_edit(document_edit_id)
        return response
