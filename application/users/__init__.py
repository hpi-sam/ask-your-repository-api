"""Provides User functionality and routes"""
from flask import Blueprint

from .users_view import UserView, UsersView
from .oauth_providers.oauth_providers_view import OAuthProvidersView, OAuthProviderView, OAuthScopes

USERS = Blueprint('users', __name__)
USERS.add_url_rule('', view_func=UsersView.as_view('usersview'))
USERS.add_url_rule('/<id>', view_func=UserView.as_view('userview'))
USERS.add_url_rule('/<id>/auth_providers', view_func=OAuthProvidersView.as_view('oauthsview'))
USERS.add_url_rule('/<id>/auth_providers/<provider>', view_func=OAuthProviderView.as_view('oauthview'))
USERS.add_url_rule('/<id>/auth_providers/<provider>/scopes', view_func=OAuthScopes.as_view('oauthscopesview'))
