from flask import Blueprint
from flask_restx import Api


main = Blueprint("main", __name__, url_prefix="/api")
api = Api(main)
