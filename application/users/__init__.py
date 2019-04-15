"""Provides User functionality and routes"""
from flask import Blueprint

from .users_view import UserView, UsersView
from .oauth.google_oauth_view import GoogleOauthView, GoogleScopesView

USERS = Blueprint("users", __name__)
USERS.add_url_rule("", view_func=UsersView.as_view("usersview"))
USERS.add_url_rule("/<id>", view_func=UserView.as_view("userview"))
USERS.add_url_rule("/<id>/oauths/google", view_func=GoogleOauthView.as_view("googleoauthview"))
USERS.add_url_rule("/<id>/oauths/google/scopes", view_func=GoogleScopesView.as_view("oauthscopesview"))
