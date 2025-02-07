from flask import request
from flask_restx import Namespace
from app.routes.base_routes import AuthorizedBaseRoute, UnauthorizedBaseRoute
from app.services.user_service import user_service, UserService
from app.dtos import (
    signup_input_dto,
    signup_output_dto,
    login_output_dto,
    login_input_dto,
    user_output_dto,
    user_update_input_dto,
)

ns = Namespace("auth", description="User Authentication related operations")


class AuthBaseRoute(UnauthorizedBaseRoute):
    service: UserService = user_service


class UserBaseRoute(AuthorizedBaseRoute):
    service: UserService = user_service


@ns.route("/signup")
@ns.response(409, "User already exists")
class SignupRoute(AuthBaseRoute):

    @ns.doc(description="Sign up a new user")
    @ns.marshal_with(signup_output_dto)
    @ns.expect(signup_input_dto)  # Use the DTO here
    def post(self):
        request_data = request.get_json()

        username = request_data.get("username")
        email = request_data.get("email")
        password = request_data.get("password")

        self.service.signup(username, email, password)
        return {"message": "User created successfully"}


@ns.route("/login")
@ns.response(401, "Unauthorized")
class LoginRoute(AuthBaseRoute):

    @ns.doc(description="Log in an existing user")
    @ns.marshal_with(login_output_dto)
    @ns.expect(login_input_dto)  # Use the DTO here
    def post(self):
        request_data = request.get_json()
        email = request_data.get("email")
        password = request_data.get("password")

        result = self.service.login(email, password)

        return result, 200


@ns.route("/update-profile")
@ns.response(200, "Profile updated successfully")
@ns.response(404, "User not found")
class UpdateProfileRoute(UserBaseRoute):

    @ns.expect(user_update_input_dto)
    @ns.marshal_with(user_output_dto)
    def put(self):
        """
        Update user profile information.

        Payload:
        - username (optional)
        - email (optional)
        - password (optional)
        """
        data = request.get_json()

        user_id = self.user_service.get_logged_in_user_id()

        updated_user = self.service.update_user_data(
            user_id,
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
        )
        return updated_user
