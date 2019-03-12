"""
Handles all logic of the user api
"""
from flask import jsonify, make_response
from flask_jwt_extended import (jwt_required, create_access_token, unset_jwt_cookies,
                                set_access_cookies, get_csrf_token)
from webargs.flaskparser import use_args

from .application_controller import ApplicationController
from ..models.user import User
from ..responders import respond_with
from ..validators import authentications_validator
from ..extensions import bcrypt


def validate_user(user, password):
    return user and bcrypt.check_password_hash(user.password, password)

class AuthenticationsController(ApplicationController):
    """ Controller for authentication """

    @use_args(authentications_validator.create_args())
    def create(self, params):
        """ Returns a cookie and a csrf token for double submit CSRF protection. """
        user = User.find_by_email_or_username(params["email_or_username"])
        if not validate_user(user, params["password"]):
            return {"error": "Bad username or password"}, 401
        return self._build_login_response(user)

    @jwt_required
    def delete(self): # pylint: disable=W0613
        """ Unsets the cookie in repsponse """
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
