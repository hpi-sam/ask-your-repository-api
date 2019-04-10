"""
Handles all logic of the password reset api
"""
import datetime
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from flask import abort, render_template
from flask.views import MethodView
from flask_apispec import MethodResource, marshal_with, use_kwargs
from flask_jwt_extended import create_access_token, decode_token
from flask_mail import Message
from application.extensions import mail
from application.responders import no_content
from application.models import User
from application.users.user_schema import USER_SCHEMA
from application.password_resets import password_resets_validator


class PasswordResets(MethodView):
    """Routes for resetting a password with a reset link."""

    @use_kwargs(password_resets_validator.create_args())
    def post(self, **params):
        user = User.find_by_email_or_username(params["email_or_username"])
        if not user:
            abort(404, "Could not find a user with that email address")
        verification = password_verification(user)
        expires = datetime.timedelta(days=1)
        payload = {"id": user.id_, "verification": verification, "purpose": "reset_password"}
        token = create_access_token(payload, expires_delta=expires)
        reset_url = set_query_parameter(params["base_url"], "reset_token", token)
        send_reset_password_email(reset_url, user)
        return no_content()

    @use_kwargs(password_resets_validator.update_args())
    @marshal_with(USER_SCHEMA)
    def put(self, **params):
        decoded_token = decode_token(params["reset_token"])
        payload = decoded_token["identity"]
        if not isinstance(payload, dict) or not payload.get("purpose") == "reset_password":
            abort(400, "Invalid password reset link")
        user = User.find(payload["id"])
        if not payload["verification"] == password_verification(user):
            abort(400, "Reset link can only be used once")
        user.update(password=params["password"])
        return user


def password_verification(user):
    """Returns the first 6 characters of the users password hash or empty string.
    It is used to check if a password reset link has already used, because the users password hash
    would have been changed."""
    return user.password[:6] if user.password else ''


def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def send_reset_password_email(password_link, recipient):
    reset_mail = Message(subject="Reset Password", recipients=[recipient.email])
    template_args = {'password_link': password_link, 'recipient': recipient.username}
    reset_mail.body = render_template('password_reset.txt', **template_args)
    reset_mail.html = render_template('password_reset.html', **template_args)
    mail.send(reset_mail)
