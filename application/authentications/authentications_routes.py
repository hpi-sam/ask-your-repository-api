"""Provides Authentication functionality and routes"""
from flask import Blueprint

from .authentications_view import AuthenticationsView

AUTHENTICATIONS = Blueprint("authentications", __name__)
AUTHENTICATIONS.add_url_rule("", view_func=AuthenticationsView.as_view("authenticationsview"))
