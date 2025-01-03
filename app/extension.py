from flask import Blueprint
from flask_restx import Api


main = Blueprint("main", __name__, url_prefix="/api")
authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
    }
}
api = Api(
    main,
    title="Annotation Project Backend API",
    version="1.0",
    doc="/docs",
    security="Bearer",
    authorizations=authorizations,
)
