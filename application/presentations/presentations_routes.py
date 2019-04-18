"""Provides presentation functionality and routes"""
from flask import Blueprint

from .presentations_view import PresentationsView

PRESENTATIONS = Blueprint("presentations", __name__)
PRESENTATIONS.add_url_rule("", view_func=PresentationsView.as_view("presentationsview"))
