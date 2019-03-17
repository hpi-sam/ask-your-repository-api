"""
Handles all logic of the user api
"""
from flask import jsonify, make_response
from flask_apispec import use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import (jwt_required, create_access_token, unset_jwt_cookies,
                                set_access_cookies, get_csrf_token)

from application.extensions import bcrypt
from application.users.user import User
from application.responders import respond_with
from application.authentications import authentications_validator


def validate_user(user, password):
    """ Validates that a password is correct for the user """
    return user and user.check_password(password)


class AuthenticationsView(MethodResource):
    """ Controller for authentication """

    @use_kwargs(authentications_validator.create_args())
    def post(self, **params):
        """ Returns a cookie and a csrf token for double submit CSRF protection. """
        user = User.find_by_email_or_username(params["email_or_username"])
        if not validate_user(user, params["password"]):
            return {"error": "Bad username or password"}, 401
        return self._build_login_response(user)

    @jwt_required
    def delete(self):  # pylint: disable=W0613
        """ Unsets the cookie in response """
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        response = make_response(resp, 200)
        response.mimetype = 'application/json'
        return response

    @staticmethod
    def _build_login_response(user):
        access_token = create_access_token(identity=user.id_, expires_delta=False)
        response = respond_with(user)
        response["token"] = get_csrf_token(access_token)
        response = jsonify(response)
        set_access_cookies(response, access_token, 10000000000)
        response = make_response(response, 200)
        response.mimetype = 'application/json'

        return response
