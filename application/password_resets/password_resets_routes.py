"""Provides User functionality and routes"""
from flask import Blueprint

from .password_resets_view import PasswordResets

PASSWORD_RESETS = Blueprint("password_resets", __name__, template_folder="templates")
PASSWORD_RESETS.add_url_rule("", view_func=PasswordResets.as_view("passwordresetsview"))
