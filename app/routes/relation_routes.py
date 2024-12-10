from app.services.relation_services import relation_service
from werkzeug.exceptions import BadRequest
from flask_restx import Namespace, Resource

ns = Namespace("relations", description="Relation related operations")


@ns.route("/<int:document_edit_id>")
@ns.doc(params={"document_edit_id": "A Document Edit ID"})
class RelationQueryResource(Resource):
    service = relation_service

    def get(self, document_edit_id):
        if not document_edit_id:
            raise BadRequest("Document Edit ID is required.")

        document_edit_id = int(document_edit_id)

        response = self.service.get_relations_by_document_edit(document_edit_id)
        return response
