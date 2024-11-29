from flask import Blueprint

main = Blueprint("main", __name__, url_prefix="/api")
project = Blueprint("projects", __name__, url_prefix="/projects")
main.register_blueprint(project)

from . import api_routes, project_routes
