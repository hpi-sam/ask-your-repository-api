"""Provides Invite link functionality and routes"""
from flask import Blueprint

from .invites_view import AcceptInvite

INVITES = Blueprint('invites', __name__)
INVITES.add_url_rule('/<join_key>', view_func=AcceptInvite.as_view('acceptinvite'))
