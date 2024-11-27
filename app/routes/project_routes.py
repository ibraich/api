from . import project
from flask import request
from app.services.project_service import project_service


@project.route("/", methods=["POST"])
def create_project():
    service = project_service
    request_data = request.get_json()
    return service.create_project(request_data)
