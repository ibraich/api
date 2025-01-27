from flask_restx import Resource
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest

from app.extension import api


@api.response(400, "Invalid input")
@api.response(500, "Internal Server Error")
class __BaseRoute(Resource):

    def verify_positive_integer(self, value):
        """
        Checks if a value is a positive integer.

        :param value: Value to check
        :exception BadRequest: If value is not a positive integer.
        """
        try:
            value = int(value)
            if value <= 0:
                raise BadRequest("Input validation failed. Value must be positive")
        except:
            raise BadRequest("Input validation failed. Value must be an integer")


@api.response(401, "Authorization required")
class AuthorizedBaseRoute(__BaseRoute):

    def dispatch_request(self, *args, **kwargs):
        jwt_required()(lambda: None)()
        return super().dispatch_request(*args, **kwargs)


class UnauthorizedBaseRoute(__BaseRoute):
    pass
