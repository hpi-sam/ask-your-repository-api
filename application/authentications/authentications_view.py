"""
Handles all logic of the user api
"""
from flask import jsonify, make_response, current_app
from flask_apispec import use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import (jwt_required, create_access_token, unset_jwt_cookies,
                                set_access_cookies, get_csrf_token)

from application.authentications import authentications_validator
from application.responders import respond_with
from application.users.user import User
from application.users.oauth_providers.oauth_provider import OAuthProvider
from application.users.oauth_providers.google_oauth import validate_google_id_token


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
            if "email_or_username" not in params:
                return {"error": "email_or_username missing"}, 422
            if "password" not in params:
                return {"error": "password missing"}, 422
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
    google_id, email = validate_google_id_token(token)
    google_auth = OAuthProvider.find_by(name='google', user_id=google_id, force=False)
    if not google_auth:
        user = User.find_by(email=email, force=False)
        if not user:
            user = User.create(email=email, username=email)
        google_auth = OAuthProvider(name='google', user_id=google_id)
        google_auth.connect(user)
        google_auth.save()
    else:
        user = google_auth.user.single()
    return user
