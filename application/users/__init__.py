""" Provides User functionality and routes """
from flask import Blueprint

from .users_view import UserView, UsersView

USERS = Blueprint('users', __name__)
USERS.add_url_rule('', view_func=UsersView.as_view('usersview'))
USERS.add_url_rule('/<id>', view_func=UserView.as_view('userview'))
