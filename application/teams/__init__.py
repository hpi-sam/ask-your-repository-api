"""Provides Team functionality and routes"""
from flask import Blueprint

from .teams_view import TeamView, TeamsView

TEAMS = Blueprint('teams', __name__)
TEAMS.add_url_rule('', view_func=TeamsView.as_view('teamsview'))
TEAMS.add_url_rule('/<id>', view_func=TeamView.as_view('teamview'))
