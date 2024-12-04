from flask import Blueprint
from flask_restx import Api
from .project_routes import api as projects
from .mention_routes import api as mentions
from .relation_routes import api as relations

main = Blueprint("main", __name__, url_prefix="/api")
api = Api(main)
api.add_namespace(projects, path="/projects")
# api.add_namespace(relations, path="/relations")
# api.add_namespace(mentions, path="/mentions")
# TODO: remove nesting, use namespaces
# project = Blueprint("projects", __name__, url_prefix="/projects")
# mentions = Blueprint("mentions", __name__, url_prefix="/mentions")
# relations = Blueprint("relations", __name__, url_prefix="/relations")
# main.register_blueprint(project)
# main.register_blueprint(mentions)
# main.register_blueprint(relations)


# from . import api_routes, project_routes, mention_routes, relation_routes
