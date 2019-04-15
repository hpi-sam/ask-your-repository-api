"""Provides Invite link functionality and routes"""
from flask import Blueprint

from .invites_view import InvitesView

INVITES = Blueprint("invites", __name__)
INVITES.add_url_rule("/<join_key>", view_func=InvitesView.as_view("acceptinvite"))
