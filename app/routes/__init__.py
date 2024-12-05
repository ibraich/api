from flask import Blueprint

main = Blueprint("main", __name__, url_prefix="/api")
project = Blueprint("projects", __name__, url_prefix="/projects")
document = Blueprint("documents", __name__, url_prefix="/documents")
mentions = Blueprint("mentions", __name__, url_prefix="/mentions")
relations = Blueprint("relations", __name__, url_prefix="/relations")
entities = Blueprint("entities", __name__, url_prefix="/entities")

main.register_blueprint(project)
main.register_blueprint(document)
main.register_blueprint(mentions)
main.register_blueprint(relations)
main.register_blueprint(entities)

from . import (
    api_routes,
    project_routes,
    document_routes,
    mention_routes,
    relation_routes,
    entity_routes
)

