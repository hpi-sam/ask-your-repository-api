"""
Handles all logic of the user api
"""
from flask import jsonify, make_response, current_app
from flask_apispec import use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import (jwt_required, create_access_token, unset_jwt_cookies,
                                set_access_cookies, get_csrf_token)
from google.oauth2 import id_token
from google.auth.transport import requests

from application.authentications import authentications_validator
from application.responders import respond_with
from application.users.user import User


def validate_user(user, password):
    """Validates that a password is correct for the user"""
    return user and user.check_password(password)


class AuthenticationsView(MethodResource):
    """Controller for authentication"""

    @use_kwargs(authentications_validator.create_args())
    def post(self, **params):
        """Returns a cookie and a csrf token for double submit CSRF protection."""
        if "id_token" in params:
            user = _get_user_from_google_token(params["id_token"])
        else:
            user = User.find_by_email_or_username(params["email_or_username"])
            if not validate_user(user, params["password"]):
                return {"error": "Bad username or password"}, 401

        return _build_login_response(user)

    @jwt_required
    def delete(self):  # pylint: disable=W0613
        """Unsets the cookie in response"""
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        response = make_response(resp, 200)
        response.mimetype = 'application/json'
        return response


def _build_login_response(user):
    access_token = create_access_token(identity=user.id_, expires_delta=False)
    response = respond_with(user)
    response["token"] = get_csrf_token(access_token)
    response = jsonify(response)
    set_access_cookies(response, access_token, 10000000000)
    response = make_response(response, 200)
    response.mimetype = 'application/json'

    return response


def _get_user_from_google_token(token):
    """Checks if a user can be obtained with the given token
    and if not, creates a new user.

    :param token: id_token returned by google login
    :return: instance of User
    """
    google_id, email = _validate_id_token(token)
    user = User.find_by(google_id=google_id, force=False)
    if not user:
        user = User.find_by(email=email, force=False)
        if not user:
            user = User.create(email=email, username=email, google_id=google_id)
    return user


def _validate_id_token(token):
    """Validates a google id_token.
    See https://developers.google.com/identity/sign-in/web/backend-auth?hl=de for reference.
    """
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['CLIENT_ID'])
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID  and email from the decoded token.
        return id_info['sub'], id_info['email']
    except ValueError:
        pass

