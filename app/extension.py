from flask import Blueprint
from flask_restx import Api


main = Blueprint("main", __name__, url_prefix="/api")
api = Api(main)

from app.routes.project_routes import ns as projects
from app.routes.mention_routes import ns as mentions
from app.routes.relation_routes import ns as relations

api.add_namespace(projects, path="/projects")
