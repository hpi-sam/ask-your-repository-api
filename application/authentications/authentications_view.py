"""
Handles all logic of the user api
"""
from flask import jsonify, make_response
from flask_apispec import use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, create_access_token, unset_jwt_cookies, set_access_cookies, get_csrf_token

from application.authentications import authentications_validator
from application.responders import respond_with
from application.users.user import User
from application.users.oauth.google_oauth import validate_google_id_token, GoogleOAuth


def validate_user(user, password):
    """Validates that a password is correct for the user"""
    return user and user.check_password(password)


class AuthenticationsView(MethodResource):
    """Controller for authentication"""

    @use_kwargs(authentications_validator.LoginSchema)
    def post(self, **params):
        """Returns a cookie and a csrf token for double submit CSRF protection."""
        if "id_token" in params:
            user = _get_user_from_google_token(params["id_token"])
        else:
            user = User.find_by_email_or_username(params["email_or_username"])
            if not validate_user(user, params["password"]):
                return {"error": "Bad username or password"}, 401

        return _build_login_response(user, params["set_cookies"])

    @jwt_required
    def delete(self):  # pylint: disable=W0613
        """Unsets the cookie in response"""
        resp = jsonify({"logout": True})
        unset_jwt_cookies(resp)
        response = make_response(resp, 200)
        response.mimetype = "application/json"
        return response


def _build_login_response(user, set_cookies):
    access_token = create_access_token(identity=user.id_, expires_delta=False)
    response = respond_with(user)
    response["csrf_token"] = get_csrf_token(access_token)
    if set_cookies:
        response = jsonify(response)
        set_access_cookies(response, access_token, 10000000000)
        response = make_response(response, 200)
        response.mimetype = "application/json"
    else:
        response["access_token"] = access_token

    return response


def _get_user_from_google_token(token):
    """Checks if a user can be obtained with the given token
    and if not, creates a new user.

    :param token: id_token returned by google login
    :return: instance of User
    """
    google_id, email = validate_google_id_token(token)
    google_auth = GoogleOAuth.find_by(user_id=google_id, force=False)
    if not google_auth:
        user = User.find_by(email=email, force=False)
        if not user:
            user = User(email=email, username=email, password=None).save()
        google_auth = GoogleOAuth(user_id=google_id).save()
        google_auth.user_rel.connect(user)  # pylint:disable=no-member
    else:
        user = google_auth.user
    return user
