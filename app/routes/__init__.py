from flask import Blueprint

main = Blueprint("main", __name__, url_prefix="/api")
project = Blueprint("projects", __name__, url_prefix="/projects")
document = Blueprint("documents", __name__, url_prefix="/documents")

main.register_blueprint(project)
main.register_blueprint(document)

from . import api_routes, project_routes, document_routes
