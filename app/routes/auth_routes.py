from flask import request
from flask_restx import Namespace, Resource
from app.services.user_service import user_service
from app.dtos import signup_input_dto, signup_output_dto

ns = Namespace("auth", description="User Authentication related operations")


@ns.route("/signup")
@ns.response(400, "Invalid input")
@ns.response(409, "User already exists")
class SignupRoute(Resource):
    service = user_service

    @ns.doc(description="Sign up a new user")
    @ns.marshal_with(signup_output_dto)
    @ns.expect(signup_input_dto, validate=True)  # Use the DTO here
    def post(self):
        request_data = request.get_json()

        username = request_data.get("username")
        email = request_data.get("email")
        password = request_data.get("password")

        self.service.signup(username, email, password)
        return {"message": "User created successfully"}