"""
Handles all logic of the password reset api
"""
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from flask import abort, render_template
from flask_apispec import MethodResource, marshal_with, use_kwargs
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt.exceptions import ExpiredSignatureError
from flask_mail import Message
from application.extensions import mail
from application.responders import no_content
from application.models import User
from application.users.user_schema import USER_SCHEMA
from application.password_resets import password_resets_validator, password_reset_jwt_manager


class PasswordResets(MethodResource):
    """Routes for resetting a password with a reset link."""

    @use_kwargs(password_resets_validator.send_reset_link_args())
    def post(self, **params):
        """Logic for sending a password reset link"""
        user = User.find_by_email_or_username(params["email_or_username"])
        if not user:
            abort(404, "Could not find a user with that email address")
        token = password_reset_jwt_manager.encode_reset_token(user)
        reset_url = set_query_parameter(params["base_url"], "reset_token", token)
        send_reset_password_email(reset_url, user)
        return no_content()

    @use_kwargs(password_resets_validator.update_password_args())
    @marshal_with(USER_SCHEMA)
    def put(self, **params):
        """Logic for changing the users password with a reset link"""
        try:
            user = password_reset_jwt_manager.get_user_from_reset_token(params["reset_token"])
            user.update(password=params["password"])
            return user
        except ExpiredSignatureError:
            abort(400, "Reset token expired")
        except JWTDecodeError as err:
            abort(400, str(err))


def set_query_parameter(url, param_name, param_value):
    """Given an URL, set or replace a query parameter and return the
    modified URL.
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def send_reset_password_email(password_link, recipient):
    """Creates the email with templates and sends it to the user"""
    reset_mail = Message(subject="Reset Password", recipients=[recipient.email])
    template_args = {"password_link": password_link, "recipient": recipient.username}
    reset_mail.body = render_template("password_reset.txt", **template_args)
    reset_mail.html = render_template("password_reset.html", **template_args)
    mail.send(reset_mail)
